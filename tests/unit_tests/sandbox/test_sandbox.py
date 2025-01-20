import unittest
from unittest.mock import MagicMock, patch

import pandas as pd
from docker.errors import ImageNotFound

from pandasai.sandbox.docker_sandbox import (
    DockerSandbox,
)


class TestDockerSandbox(unittest.TestCase):
    def setUp(self):
        self.image_name = "test_image"
        self.dfs = [MagicMock()]

    @patch("pandasai.sandbox.docker_sandbox.docker.from_env")
    def test_image_exists(self, mock_docker):
        sandbox = DockerSandbox(image_name=self.image_name)
        mock_client = mock_docker.return_value
        mock_client.images.get.return_value = True
        self.assertTrue(sandbox._image_exists())

        mock_client.images.get.side_effect = ImageNotFound("Image not found")
        self.assertFalse(sandbox._image_exists())

    @patch("pandasai.sandbox.docker_sandbox.docker.from_env")
    def test_build_image(self, mock_docker):
        sandbox = DockerSandbox(image_name=self.image_name)
        mock_client = mock_docker.return_value
        sandbox._build_image()
        mock_client.images.build.assert_called_once_with(
            path=sandbox.dockerfile_path, tag=self.image_name
        )

    @patch("pandasai.sandbox.docker_sandbox.docker.from_env")
    def test_start_and_stop_container(self, mock_docker):
        sandbox = DockerSandbox(image_name=self.image_name)
        mock_client = mock_docker.return_value
        mock_client.containers = MagicMock()
        mock_client.containers.run = MagicMock(return_value=MagicMock())

        sandbox.start()
        mock_client.containers.run.assert_called_once_with(
            self.image_name, command="sleep infinity", detach=True, tty=True
        )

        sandbox.stop()
        self.assertIsNone(sandbox.container)

    def test_extract_sql_queries_from_code(self):
        sandbox = DockerSandbox(image_name=self.image_name)
        code = """
sql_query = 'SELECT COUNT(*) FROM table'
result = execute_sql_query(sql_query)
        """
        queries = sandbox.extract_sql_queries_from_code(code)
        self.assertEqual(queries, ["SELECT COUNT(*) FROM table"])

    @patch("pandasai.sandbox.docker_sandbox.docker.from_env")
    def test_pass_csv(self, mock_docker):
        sandbox = DockerSandbox(image_name=self.image_name)
        mock_client = mock_docker.return_value
        mock_container = mock_client.containers.run.return_value
        sandbox.container = mock_container

        df = pd.DataFrame({"col1": [1, 2, 3], "col2": [4, 5, 6]})
        sandbox.pass_csv(df, filename="test.csv")

        mock_container.put_archive.assert_called()

    @patch("pandasai.sandbox.docker_sandbox.docker.from_env")
    def test_exec_code(self, mock_docker):
        sandbox = DockerSandbox(image_name=self.image_name)
        mock_client = mock_docker.return_value
        mock_container = mock_client.containers.run.return_value
        mock_container.exec_run.return_value = (
            0,
            (b'{"type": "number", "value": 42}', b""),
        )
        sandbox.container = mock_container

        code = 'result = {"type": "number", "value": 42}'
        result = sandbox._exec_code(code, dfs=self.dfs)
        self.assertEqual(result, {"type": "number", "value": 42})

    @patch("pandasai.sandbox.docker_sandbox.docker.from_env")
    def test_exec_code_with_sql_queries(self, mock_docker):
        sandbox = DockerSandbox(image_name=self.image_name)
        mock_client = mock_docker.return_value
        mock_container = mock_client.containers.run.return_value
        mock_container.exec_run.return_value = (
            0,
            (b'{"type": "number", "value": 42}', b""),
        )
        sandbox.container = mock_container

        # Mock SQL execution
        mock_df = pd.DataFrame({"total_artists": [42]})
        self.dfs[0].execute_sql_query.return_value = mock_df

        code = """
sql_query = 'SELECT COUNT(DISTINCT Artist) AS total_artists FROM artists'
total_artists_df = execute_sql_query(sql_query)
total_artists = total_artists_df['total_artists'].iloc[0]
result = {'type': 'number', 'value': total_artists}
        """
        result = sandbox._exec_code(code, dfs=self.dfs)
        self.assertEqual(result, {"type": "number", "value": 42})


if __name__ == "__main__":
    unittest.main()
