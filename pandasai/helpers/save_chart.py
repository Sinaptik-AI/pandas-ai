"""Helper functions to save charts to a file, if plt.show() is called."""
import ast
import os
from datetime import datetime
from itertools import zip_longest
from os.path import dirname
from typing import Union

import astor


def compare_ast(
    node1: Union[ast.expr, list[ast.expr], ast.stmt, ast.AST],
    node2: Union[ast.expr, list[ast.expr], ast.stmt, ast.AST],
    ignore_args=False,
) -> bool:
    """Compare two AST nodes for equality.
    Source: https://stackoverflow.com/a/66733795/11080806"""
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


def add_save_chart(code: str) -> str:
    """Add line to code that save charts to a file, if plt.show() is called."""
    date = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    # define chart save directory
    project_root = dirname(dirname(dirname(__file__)))
    chart_save_dir = os.path.join(project_root, f"exports\\charts\\{date}")
    if not os.path.exists(chart_save_dir):
        os.makedirs(chart_save_dir)

    tree = ast.parse(code)

    # count number of plt.show() calls
    show_count = sum(
        compare_ast(node, ast.parse("plt.show()").body[0], ignore_args=True)
        for node in ast.walk(tree)
    )

    # if there are no plt.show() calls, return the original code
    if show_count == 0:
        return code

    # iterate through the AST and add plt.savefig() calls before plt.show() calls
    counter = ord("a")
    new_body = []
    for node in tree.body:
        if compare_ast(node, ast.parse("plt.show()").body[0], ignore_args=True):
            filename = f"chart_{timestamp}"
            if show_count > 1:
                filename += f"_{chr(counter)}"
                counter += 1
            new_body.append(
                ast.parse(f"plt.savefig(r'{chart_save_dir}\\{filename}.png')")
            )
        new_body.append(node)

    new_body.append(ast.parse(f"print(r'Charts saved to: {chart_save_dir}')"))

    new_tree = ast.Module(body=new_body)
    return astor.to_source(new_tree).strip()
