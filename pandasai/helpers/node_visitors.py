import ast


class CallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.call_nodes = []

    def visit_Call(self, node):  # noqa: N802
        self.call_nodes.append(node)
        self.generic_visit(node)
