import os
import re


def find_project_root(filename=None):
    """
    Check if Custom workspace path provide use that otherwise iterate to
    find project root
    """

    # Get the path of the file that is be
    # ing executed

    current_file_path = os.path.abspath(os.getcwd())

    # Navigate back until we either find a $filename file or there is no parent
    # directory left.
    root_folder = current_file_path
    while True:
        # Custom way to identify the project root folder
        if filename is not None:
            env_file_path = os.path.join(root_folder, filename)
            if os.path.isfile(env_file_path):
                break

        # Most common ways to identify a project root folder
        if (
            os.path.isfile(os.path.join(root_folder, "pyproject.toml"))
            or os.path.isfile(os.path.join(root_folder, "setup.py"))
            or os.path.isfile(os.path.join(root_folder, "requirements.txt"))
        ):
            break

        parent_folder = os.path.dirname(root_folder)
        if parent_folder == root_folder:
            # if project root is not found return cwd
            return os.getcwd()

        root_folder = parent_folder

    return root_folder


def find_closest(filename):
    return os.path.join(find_project_root(filename), filename)


def get_validated_dataset_path(path: str):
    # Validate path format
    path_parts = path.split("/")
    if len(path_parts) != 2:
        raise ValueError("Path must be in format 'organization/dataset'")

    org_name, dataset_name = path_parts
    if not org_name or not dataset_name:
        raise ValueError("Both organization and dataset names are required")

    # Validate organization and dataset name format
    if not bool(re.match(r"^[a-z0-9\-_]+$", org_name)):
        raise ValueError(
            "Organization name must be lowercase and use hyphens instead of spaces (e.g. 'my-org')"
        )

    if not bool(re.match(r"^[a-z0-9\-_]+$", dataset_name)):
        raise ValueError(
            "Dataset name must be lowercase and use hyphens instead of spaces (e.g. 'my-dataset')"
        )

    return org_name, dataset_name
