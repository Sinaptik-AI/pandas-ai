import os


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
