import ast
import io
import os
import tarfile
import uuid

import docker

from .sandbox import Sandbox


class DockerSandbox(Sandbox):
    def __init__(self, image_name, dockerfile_path=None):
        super().__init__()
        self.dockerfile_path = dockerfile_path or os.path.join(
            os.path.dirname(__file__)
        )
        self.image_name = image_name
        self.client = docker.from_env()
        self.container = None

        # Build the image if it does not exist
        if not self._image_exists():
            self._build_image()

    def _image_exists(self):
        try:
            self.client.images.get(self.image_name)
            return True
        except docker.errors.ImageNotFound:
            return False

    def _build_image(self):
        print(
            f"Building Docker image '{self.image_name}' from '{self.dockerfile_path}'..."
        )
        self.client.images.build(path=self.dockerfile_path, tag=self.image_name)

    def start(self):
        if not self.started:
            self.container = self.client.containers.run(
                self.image_name, command="sleep infinity", detach=True, tty=True
            )
            self.started = True

    def stop(self):
        if self.started and self.container:
            self.container.stop()
            self.container.remove()
            self.container = None
            self.started = False

    def extract_sql_queries_from_code(self, code):
        """
        Extract SQL query strings from Python code

        Args:
            code (str): Python code as a string.

        Returns:
            list: List of SQL query strings found in the code.
        """
        sql_queries = []

        class SQLQueryExtractor(ast.NodeVisitor):
            def visit_Assign(self, node):
                # Look for assignments where SQL queries might be defined
                if isinstance(
                    node.value, (ast.Str, ast.Constant)
                ):  # Python 3.8+: ast.Constant
                    if "SELECT" in node.value.s.upper():
                        sql_queries.append(node.value.s)
                self.generic_visit(node)

            def visit_Call(self, node):
                # Look for function calls where SQL queries might be passed
                for arg in node.args:
                    if isinstance(
                        arg, (ast.Str, ast.Constant)
                    ):  # Python 3.8+: ast.Constant
                        if "SELECT" in arg.s.upper():
                            sql_queries.append(arg.s)
                self.generic_visit(node)

        # Parse the code into an AST and visit all nodes
        tree = ast.parse(code)
        SQLQueryExtractor().visit(tree)

        return sql_queries

    def _exec_code(self, code, dfs):
        if not self.container:
            raise RuntimeError("Container is not running.")

        sql_queries = self.extract_sql_queries_from_code(code)

        datasets_map = {}
        for sql_query in sql_queries:
            query_df = dfs[0].execute_sql_query(sql_query)
            filename = f"{uuid.uuid4().hex}.csv"
            self.pass_csv(query_df, filename=filename)
            datasets_map[sql_query] = filename

        exit_code, output = self.container.exec_run(
            cmd=f'python -c "{code}"', demux=True
        )

        # sql_query = "SELECT ...."
        # list []
        # result = execute_sql_query("....")
        # ...
        # {
        #     ...
        # }
        # def execute_sql_query(sql_query):

        #     return pd.read_csv(filepath)

        # result = execute_sql_query(sql_query)
        # orginal
        # ...

        if exit_code != 0:
            raise RuntimeError(f"Error executing code: {output[1].decode()}")
        return output[0].decode()

    def pass_csv(self, csv_data, filename="file.csv"):
        if not self.container:
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
        self.container.put_archive("/tmp", tar_stream)
