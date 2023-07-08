"""Helper functions to save charts to a file, if plt.show() is called."""
import ast
import logging
import os
from itertools import zip_longest
from os.path import dirname
from typing import Union

import astor


def compare_ast(
    node1: Union[ast.expr, list[ast.expr], ast.stmt, ast.AST],
    node2: Union[ast.expr, list[ast.expr], ast.stmt, ast.AST],
    ignore_args=False,
) -> bool:
    """
    Compare two AST nodes for equality.
    Source: https://stackoverflow.com/a/66733795/11080806

    Args:
        node1 (ast.AST): First AST node to compare.
        node2 (ast.AST): Second AST node to compare.
        ignore_args (bool, optional): Whether to ignore the arguments of the nodes.
            Defaults to False.

    Returns:
        bool: True if the nodes are equal, False otherwise.

    """
    if type(node1) is not type(node2):
        return False

    if isinstance(node1, ast.AST):
        for k, node in vars(node1).items():
            if k in {"lineno", "end_lineno", "col_offset", "end_col_offset", "ctx"}:
                continue
            if ignore_args and k == "args":
                continue
            if not compare_ast(node, getattr(node2, k), ignore_args):
                return False
        return True

    if isinstance(node1, list) and isinstance(node2, list):
        return all(
            compare_ast(n1, n2, ignore_args) for n1, n2 in zip_longest(node1, node2)
        )

    return node1 == node2


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
    show_count = sum(
        compare_ast(node, ast.parse("plt.show()").body[0], ignore_args=True)
        for node in ast.walk(tree)
    )

    # if there are no plt.show() calls, return the original code
    if show_count == 0:
        return code

    if not os.path.exists(chart_save_dir):
        os.makedirs(chart_save_dir)

    # iterate through the AST and add plt.savefig() calls before plt.show() calls
    counter = ord("a")
    new_body = []
    for node in tree.body:
        if compare_ast(node, ast.parse("plt.show()").body[0], ignore_args=True):
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
