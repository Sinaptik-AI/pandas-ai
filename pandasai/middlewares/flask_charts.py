"""
Flask Charts Middleware class

Middleware to handle the charts for Flask apps in PandasAI.
"""

from pandasai.middlewares.base import Middleware
import ast
from ast import *
import logging


class FlaskChartsMiddleware(Middleware):
    """Flask Charts Middleware class"""

    def run(self, code: str) -> str:
        """
        Run the middleware to remove issues with displaying charts in PandasAI.

        Returns:
            str: Modified code
        """

        if "plt.show()" in code:
            # PrintAllCalls().visit(ast.parse(code))

            tree = ast.parse(code)
            transformer = TransformMatplotlibAST()
            new_tree = transformer.visit(tree)
            code = ast.unparse(new_tree)
            # transformer.logger.info(code)
            
        return code



class TransformMatplotlibAST(NodeTransformer):
    def __init__(self):
        self.encountered_savefig = False
        self.savefig_added = False

        self.logger = logging.getLogger('flask_charts')
        self.logger.setLevel(logging.DEBUG)  # Set the minimum logged level to DEBUG

        # Create a file handler
        handler = logging.FileHandler('flask_charts.log')
        handler.setLevel(logging.DEBUG)  # Set the minimum logged level to DEBUG

        # Create a formatter and add it to the handler
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(handler)


        super().__init__()

    def visit_Expr(self, node):
        call = node.value
        if isinstance(call, Call) and isinstance(call.func, Attribute):
            attr = call.func
            if isinstance(attr.value, Name) and attr.value.id == "plt":
                function_args = ", ".join(ast.unparse(arg) for arg in call.args)
                # consider plt function calls with more than one argument as plot functions
                if len(call.args) > 1:
                    new_code = "\nfig = Figure()\nax = fig.subplots()\nax.{}({})".format(attr.attr, function_args)
                    return parse(new_code).body
                elif attr.attr == "title": 
                    title_args = ast.unparse(call.args[0]) if call.args else ''
                    return parse("ax.set_title({})".format(title_args)).body
                elif attr.attr == "xlabel":
                    xlabel_args = ast.unparse(call.args[0]) if call.args else ''
                    return parse("ax.set_xlabel({})".format(xlabel_args)).body
                elif attr.attr == "ylabel":
                    ylabel_args = ast.unparse(call.args[0]) if call.args else ''
                    return parse("ax.set_ylabel({})".format(ylabel_args)).body
                elif attr.attr == "savefig":
                    self.encountered_savefig = True
                elif attr.attr == "show" or attr.attr == "close":
                    if not self.encountered_savefig:
                        self.encountered_savefig = True
        return node

    def visit_Module(self, node):
        # add necessary import statements at the start of the module
        import_stmts = parse("import base64\nfrom io import BytesIO\nfrom matplotlib.figure import Figure").body
        transformed_body = [self.visit(n) for n in node.body]
        if self.encountered_savefig and not self.savefig_added:
            transformed_body.extend(parse("\nbuf = BytesIO()\nfig.savefig(buf, format='png')\ndata = base64.b64encode(buf.getbuffer()).decode('ascii')\nprint(f'<img src=\"data:image/png;base64,{data}\"/>')").body)
            self.savefig_added = True
        return Module(body=import_stmts + transformed_body, type_ignores=node.type_ignores)

class PrintAllCalls(NodeVisitor):
    def visit_Call(self, node):
        transformer = TransformMatplotlibAST()
        transformer.logger.info(ast.unparse(node))
        # print(ast.unparse(node))
        self.generic_visit(node)
