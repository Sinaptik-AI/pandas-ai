import io
import logging
import os
import re
import tarfile
import uuid
from typing import Optional

import docker

from pandasai.sandbox import Sandbox

from .serializer import ResponseSerializer

logger = logging.getLogger(__name__)


class DockerSandbox(Sandbox):
    def __init__(self, image_name="pandaai-sandbox", dockerfile_path=None):
        super().__init__()
        self._dockerfile_path: str = dockerfile_path or os.path.join(
            os.path.dirname(__file__), "Dockerfile"
        )
        self._image_name: str = image_name
        self._client: docker.DockerClient = docker.from_env()
        self._container: Optional[docker.models.containers.Container] = None

        # Build the image if it does not exist
        if not self._image_exists():
            self._build_image()

        self._helper_code: str = self._read_start_code(
            os.path.join(os.path.dirname(__file__), "serializer.py")
        )

    def _image_exists(self) -> bool:
        try:
            self._client.images.get(self._image_name)
            return True
        except docker.errors.ImageNotFound:
            return False

    def _build_image(self) -> None:
        logger.info(
            f"Building Docker image '{self._image_name}' from '{self._dockerfile_path}'..."
        )
        with open(self._dockerfile_path, "rb") as file:
            self._client.images.build(fileobj=file, tag=self._image_name)

    def start(self):
        if not self._started:
            logger.info(
                f"Starting a Docker container from the image '{self._image_name}'"
            )
            self._container = self._client.containers.run(
                self._image_name,
                command="sleep infinity",
                network_disabled=True,
                detach=True,
                tty=True,
            )
            logger.info(
                f"Started a Docker container with id '{self._container.id}' from the image '{self._image_name}'"
            )
            self._started = True

    def stop(self) -> None:
        if self._started and self._container:
            logger.info(f"Stopping a Docker container with id '{self._container.id}''")
            self._container.stop()
            self._container.remove()
            self._container = None
            self._started = False

    def _read_start_code(self, file_path: str) -> str:
        """Read helper start code from a file as a string.

        Args:
            file_path (str): Path to the file.

        Returns:
            str: Code as a string.
        """
        with open(file_path, "r") as file:
            return file.read()

    def _exec_code(self, code: str, environment: dict) -> dict:
        """Execute Python code in a Docker container.

        Args:
            code (str): Code to execute.
            environment (dict): Environment variables to pass to the container.

        Returns:
            dict: Result of the code execution.
        """
        if not self._container:
            raise RuntimeError("Container is not running.")

        sql_queries = self._extract_sql_queries_from_code(code)

        # Temporary chart storage path
        chart_path = "/tmp/temp_chart.png"
        # actual chart path
        original_chart_path = None

        if png_paths := re.findall(r"'([^']+\.png)'", code):
            original_chart_path = png_paths[0]

        # update chart path
        code = re.sub(
            r"""(['"])([^'"]*\.png)\1""",
            lambda m: f"{m.group(1)}{chart_path}{m.group(1)}",
            code,
        )

        # Execute SQL queries, save the query results to CSV files
        datasets_map = {}
        for sql_query in sql_queries:
            execute_sql_query_func = environment.get("execute_sql_query")
            if execute_sql_query_func is None:
                raise RuntimeError(
                    "execute_sql_query function is not defined in the environment."
                )

            query_df = execute_sql_query_func(sql_query)
            filename = f"{uuid.uuid4().hex}.csv"
            # Pass the files to the container for further processing
            self.transfer_file(query_df, filename=filename)
            datasets_map[sql_query] = filename

        # Add the datasets_map variable to the code
        dataset_map = f"""
datasets_map = {datasets_map}

def execute_sql_query(sql_query):
    filename = datasets_map[sql_query]
    filepath = os.path.join("/tmp", filename)
    return pd.read_csv(filepath)

"""
        # serialization code to get output from docker
        end_code = """
print(parser.serialize(result))
"""
        # Concatenate code and helper code
        code = self._helper_code + dataset_map + code + end_code

        # Compile the code for errors
        self._compile_code(code)

        # Replace double quotes with escaped double quotes for command line code arguments
        code = code.replace('"', '\\"')

        logger.info(f"Submitting code to docker container {code}")

        exit_code, output = self._container.exec_run(
            cmd=f'python -c "{code}"', demux=True
        )

        if exit_code != 0:
            raise RuntimeError(f"Error executing code: {output[1].decode()}")

        response = output[0].decode()
        return ResponseSerializer.deserialize(response, original_chart_path)

    def transfer_file(self, csv_data, filename="file.csv") -> None:
        if not self._container:
            raise RuntimeError("Container is not running.")

        # Convert the DataFrame to a CSV string
        csv_string = csv_data.to_csv(index=False)

        # Create a tar archive in memory
        tar_stream = io.BytesIO()
        with tarfile.open(fileobj=tar_stream, mode="w") as tar:
            # Add the CSV string as a file in the tar archive
            csv_bytes = csv_string.encode("utf-8")
            tarinfo = tarfile.TarInfo(name=filename)
            tarinfo.size = len(csv_bytes)
            tar.addfile(tarinfo, io.BytesIO(csv_bytes))

        # Seek to the beginning of the stream
        tar_stream.seek(0)

        # Transfer the tar archive to the container
        self._container.put_archive("/tmp", tar_stream)

    def __del__(self) -> None:
        if self._container:
            self._container.stop()
            self._container.remove()
