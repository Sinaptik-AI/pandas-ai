"""Unit tests for the save_chart module."""
import ast
import os.path

from pandasai.helpers.save_chart import add_save_chart, is_show_node


class TestSaveChart:
    """Unit tests for the save_chart module."""

    def test_is_show_node(self):
        node1 = ast.parse("plt.show()").body[0]
        node2 = ast.parse("plt.show(*some-args)").body[0]
        node3 = ast.parse("print(r'hello/word.jpeg')").body[0]
        node4 = ast.parse("print()").body[0]

        assert is_show_node(node1)
        assert is_show_node(node2)
        assert not is_show_node(node3)
        assert not is_show_node(node4)

    def test_save_chart(self):
        chart_code = """
import matplotlib.pyplot as plt
import pandas as pd
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
df.plot()
plt.show()
"""
        line_count = len(ast.parse(chart_code).body)
        tree = ast.parse(add_save_chart(chart_code, "test_folder"))
        show_call_pos = [i for i, node in enumerate(tree.body) if is_show_node(node)][0]
        assert len(tree.body) == line_count + 1
        assert tree.body[show_call_pos - 1].value.func.value.id == "plt"
        assert tree.body[show_call_pos - 1].value.func.attr == "savefig"

    def test_save_chart_with_args(self):
        chart_code = """
import matplotlib.pyplot as plt
import pandas as pd
df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
df.plot()
plt.show(block=False)
"""
        line_count = len(ast.parse(chart_code).body)
        tree = ast.parse(add_save_chart(chart_code, "test_folder"))
        assert len(tree.body) == line_count + 1
        show_call_pos = [i for i, node in enumerate(tree.body) if is_show_node(node)][0]
        assert tree.body[show_call_pos - 1].value.func.value.id == "plt"
        assert tree.body[show_call_pos - 1].value.func.attr == "savefig"

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
        line_count = len(ast.parse(chart_code).body)
        tree = ast.parse(add_save_chart(chart_code, "test_folder"))
        show_call_pos = [i for i, node in enumerate(tree.body) if is_show_node(node)]

        assert len(tree.body) == line_count + 2

        # check first node is plt.savefig() and filename ends with a
        actual_node = tree.body[show_call_pos[0] - 1]
        assert tree.body[show_call_pos[0] - 1].value.func.value.id == "plt"
        assert tree.body[show_call_pos[0] - 1].value.func.attr == "savefig"
        actual_node_args = [a.value for a in actual_node.value.args]
        assert os.path.splitext(actual_node_args[0])[0][-1] == "a"

        # check second node is plt.savefig() and filename ends with n
        actual_node = tree.body[show_call_pos[1] - 1]
        assert tree.body[show_call_pos[1] - 1].value.func.value.id == "plt"
        assert tree.body[show_call_pos[1] - 1].value.func.attr == "savefig"
        actual_node_args = [a.value for a in actual_node.value.args]
        assert os.path.splitext(actual_node_args[0])[0][-1] == "b"
