"""
This module contains helper functions for generating plots.
"""


def is_code_for_plots(code: str,plt_code: str, plot_keywords: list[str]) -> bool:
    no_plt = code.count(plt_code) < 1
    return any(keyword_generator(code, plot_keywords)) and no_plt


def keyword_generator(code: str, plot_keywords: list[str]):
    for x in plot_keywords:
        yield x in code
