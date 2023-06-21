"""
Flask Charts Middleware class

Middleware to handle the charts for Flask apps in PandasAI.
"""

from pandasai.middlewares.base import Middleware
import ast
from ast import *


class FlaskChartsMiddleware(Middleware):
    """Flask Charts Middleware class"""

    def run(self, code: str) -> str:
        """
        Run the middleware to remove issues with displaying charts in PandasAI.

        Returns:
            str: Modified code
        """

        if "plt.show()" in code:
            tree = ast.parse(code)
            transformer = TransformMatplotlibAST()
            new_tree = transformer.visit(tree)
            code = ast.unparse(new_tree)

            
        return code



class TransformMatplotlibAST(NodeTransformer):
    def visit_Expr(self, node):
        call = node.value
        if isinstance(call, Call) and isinstance(call.func, Attribute):
            attr = call.func
            if isinstance(attr.value, Name) and attr.value.id == "plt":
                if attr.attr == "plot":
                    return parse("""
                    fig = Figure()
                    ax = fig.subplots()
                    ax.plot({args})
                    """.format(args=", ".join(map(to_source, call.args)))).body
                elif attr.attr == "title": 
                    
                    return parse("""
                    ax.set_title({args}
                    """.format()).body
                elif attr.attr == "xlabel":
                    return parse("""
                    ax.set_xlabel({args}
                    """.format()).body
                elif attr.attr == "ylabel":
                    return parse("""
                    ax.set_ylabel({args}
                    """.format()).body
                elif attr.attr == "savefig":
                    return parse("""
                    buf = BytesIO()
                    fig.savefig(buf, format="png")
                    data = base64.b64encode(buf.getbuffer()).decode("ascii")
                    print(f"<img src='data:image/png;base64,{data}'/>")
                    """.format()).body
                elif attr.attr == "show" or attr.attr == "close":
                    # Ignore these as they're not relevant in the new code
                    pass
        return node

def to_source(node):
    if isinstance(node, ast.AST):
        node = astor.to_source(node)
        if node.endswith('\n'):
            node = node[:-1]
    return node


