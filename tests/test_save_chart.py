"""Unit tests for the save_chart module."""
import ast
import os.path

from pandasai.helpers.save_chart import add_save_chart, compare_ast


class TestSaveChart:
    """Unit tests for the save_chart module."""

    def test_compare_ast(self):
        node1 = ast.parse("plt.show()").body[0]
        node2 = ast.parse("plt.show(*some-args)").body[0]
        assert compare_ast(node1, node2, ignore_args=True)

    def test_save_chart(self):
        chart_code = """
import matplotlib.pyplot as plt
import pandas as pd
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
df.plot()
plt.show()
"""
        tree = ast.parse(add_save_chart(chart_code))
        expected_node = ast.parse("plt.savefig()").body[0]
        assert len(tree.body) == 6
        assert compare_ast(tree.body[-2], expected_node, ignore_args=True)

    def test_save_multiple_charts(self):
        chart_code = """
import matplotlib.pyplot as plt
import pandas as pd
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
df.plot('a')
plt.show()
df.plot('b')
plt.show()
"""
        tree = ast.parse(add_save_chart(chart_code))
        expected_node = ast.parse("plt.savefig()").body[0]

        assert len(tree.body) == 9

        # check first node is plt.savefig() and filename ends with a
        actual_node = tree.body[-5]
        assert compare_ast(actual_node, expected_node, ignore_args=True)
        actual_node_args = [a.value for a in actual_node.value.args]
        assert os.path.splitext(actual_node_args[0])[0][-1] == "a"

        # check second node is plt.savefig() and filename ends with n
        actual_node = tree.body[-2]
        assert compare_ast(actual_node, expected_node, ignore_args=True)
        actual_node_args = [a.value for a in actual_node.value.args]
        assert os.path.splitext(actual_node_args[0])[0][-1] == "b"
