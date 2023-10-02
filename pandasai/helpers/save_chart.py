"""Helper functions to save charts to a file, if plt.show() is called."""
from .logger import Logger
from os import makedirs, path


def add_save_chart(
    code: str,
    logger: Logger,
    file_name: str,
    save_charts_path: str = None,
) -> str:
    """
    Add line to code that save charts to a file, if plt.show() is called.

    Args:
        code (str): Code to add line to.
        logger (logging.Logger): Logger to use.
        file_name (str): Name of folder to save charts to.
        save_charts_path (str): User Defined Path to save Charts

    Returns:
        str: Code with line added.

    """
    if save_charts_path is not None:
        if not path.exists(save_charts_path):
            makedirs(save_charts_path)

        save_charts_file = path.join(save_charts_path, file_name + ".png")
        code = code.replace("temp_chart.png", save_charts_file)
        logger.log(f"Saving charts to {save_charts_file}")

    return code
