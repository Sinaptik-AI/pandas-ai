import ast


class AssignmentVisitor(ast.NodeVisitor):
    def __init__(self):
        self.assignment_nodes = []

    def visit_Assign(self, node):  # noqa: N802
        self.assignment_nodes.append(node)
        self.generic_visit(node)


class CallVisitor(ast.NodeVisitor):
    def __init__(self):
        self.call_nodes = []

    def visit_Call(self, node):  # noqa: N802
        self.call_nodes.append(node)
        self.generic_visit(node)
