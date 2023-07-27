"""Helper functions to save charts to a file, if plt.show() is called."""
import ast
import logging
import os
from os.path import dirname

import astor


def is_show_node(node: ast.Call) -> bool:
    if not hasattr(node, "value"):
        return False

    value = node.value
    return (
        isinstance(value, ast.Call)
        and value.func
        and (
            isinstance(value.func, ast.Attribute)
            and value.func.attr == "show"
            and value.func.value.id == "plt"
        )
    )


def add_save_chart(
    code: str,
    folder_name: str,
    save_charts_path: str = None,
    print_save_dir: bool = True,
) -> str:
    """
    Add line to code that save charts to a file, if plt.show() is called.

    Args:
        code (str): Code to add line to.
        folder_name (str): Name of folder to save charts to.
        save_charts_path (str): User Defined Path to save Charts
        print_save_dir (bool): Print the save directory to the console.
            Defaults to True.

    Returns:
        str: Code with line added.

    """

    if save_charts_path is not None:
        charts_root_dir = save_charts_path
    else:
        # define chart save directory
        charts_root_dir = dirname(dirname(dirname(__file__)))

    chart_save_dir = os.path.join(charts_root_dir, "exports", "charts", folder_name)

    tree = ast.parse(code)

    # count number of plt.show() calls
    show_count = sum(1 for node in ast.walk(tree) if is_show_node(node))

    # if there are no plt.show() calls, return the original code
    if show_count == 0:
        return code

    if not os.path.exists(chart_save_dir):
        os.makedirs(chart_save_dir)

    # iterate through the AST and add plt.savefig() calls before plt.show() calls
    counter = ord("a")
    new_body = []
    for node in tree.body:
        if is_show_node(node):
            filename = "chart"
            if show_count > 1:
                filename += f"_{chr(counter)}"
                counter += 1

            chart_save_path = os.path.join(chart_save_dir, f"{filename}.png")
            new_body.append(ast.parse(f"plt.savefig(r'{chart_save_path}')"))
        new_body.append(node)

    chart_save_msg = f"Charts saving to: {chart_save_dir}"
    if print_save_dir:
        print(chart_save_msg)
    logging.info(chart_save_msg)

    new_tree = ast.Module(body=new_body)
    return astor.to_source(new_tree, pretty_source=lambda x: "".join(x)).strip()
