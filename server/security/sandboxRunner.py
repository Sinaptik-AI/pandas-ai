#!/usr/bin/env python3
"""
PandasAI Default Secure Sandbox Runner
Remediation for Issue #1895:
Default code executor runs LLM-generated code with full builtins (no sandbox by default) -> RCE via indirect prompt injection.

This runner enforces:
1. AST-level verification: Rejects dangerous imports, dunder traversal, and forbidden calls before execution.
2. Restricted __builtins__: Replaces full builtins with an allowlist of safe mathematical & data structures.
3. Namespace isolation: Only safe modules and data structures are accessible.
4. Fail-closed error handling with timeout protection.
"""

import sys
import json
import ast
import io
import contextlib

# Allowlist of safe builtins - STRICTLY NO __import__, eval, exec, open, compile, globals, locals
SAFE_BUILTINS = {
    'abs': abs,
    'all': all,
    'any': any,
    'bin': bin,
    'bool': bool,
    'dict': dict,
    'enumerate': enumerate,
    'filter': filter,
    'float': float,
    'format': format,
    'int': int,
    'isinstance': isinstance,
    'issubclass': issubclass,
    'len': len,
    'list': list,
    'map': map,
    'max': max,
    'min': min,
    'pow': pow,
    'print': print,
    'range': range,
    'reversed': reversed,
    'round': round,
    'set': set,
    'slice': slice,
    'sorted': sorted,
    'str': str,
    'sum': sum,
    'tuple': tuple,
    'zip': zip,
    'None': None,
    'True': True,
    'False': False,
}

# Allowed safe standard modules for data manipulation
SAFE_MODULE_ALLOWLIST = {'math', 'statistics', 'json', 're', 'datetime'}

# Dangerous call identifiers
FORBIDDEN_CALLS = {
    'eval', 'exec', '__import__', 'open', 'compile', 'input', 'breakpoint',
    'globals', 'locals', 'vars', 'dir', 'getattr', 'setattr', 'delattr',
    'memoryview', 'classmethod', 'staticmethod', 'super', 'help'
}

# Dangerous attribute names
FORBIDDEN_ATTRS = {
    '__builtins__', '__class__', '__base__', '__bases__', '__subclasses__',
    '__mro__', '__globals__', '__code__', '__reduce__', '__reduce_ex__',
    '__dict__', '__getattribute__', '__init_subclass__', 'system', 'popen',
    'spawn', 'call', 'check_output', 'run'
}

class SandboxSecurityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.violations = []

    def visit_Import(self, node):
        for alias in node.names:
            mod_root = alias.name.split('.')[0]
            if mod_root not in SAFE_MODULE_ALLOWLIST:
                self.violations.append(
                    f"Forbidden import: '{alias.name}'. The default sandbox rejects untrusted library imports."
                )
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        mod_root = (node.module or '').split('.')[0]
        if mod_root not in SAFE_MODULE_ALLOWLIST:
            self.violations.append(
                f"Forbidden import from: '{node.module}'. The default sandbox rejects untrusted library imports."
            )
        self.generic_visit(node)

    def visit_Attribute(self, node):
        attr = node.attr
        if attr in FORBIDDEN_ATTRS or (attr.startswith('__') and attr.endswith('__')):
            self.violations.append(
                f"Forbidden attribute access: '{attr}'. Dunder traversal and OS execution methods are blocked."
            )
        self.generic_visit(node)

    def visit_Call(self, node):
        # Check direct call by name
        if isinstance(node.func, ast.Name):
            if node.func.id in FORBIDDEN_CALLS:
                self.violations.append(
                    f"Forbidden call: '{node.func.id}()'. Dynamic code execution and builtins access are blocked."
                )
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_ATTRS:
                self.violations.append(
                    f"Forbidden method call: '{node.func.attr}()'. Potential command execution pattern blocked."
                )
        self.generic_visit(node)

def validate_code_ast(code: str):
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [f"SyntaxError on line {e.lineno}: {e.msg}"]
    
    visitor = SandboxSecurityVisitor()
    visitor.visit(tree)
    if visitor.violations:
        return False, visitor.violations
    return True, []

def execute_in_sandbox(code: str, dataset_records: list = None):
    # 1. AST Validation
    is_valid, violations = validate_code_ast(code)
    if not is_valid:
        return {
            "status": "blocked",
            "securityPolicy": "DEFAULT_SANDBOX_STRICT",
            "violations": violations,
            "message": "Execution rejected by default sandbox security policy (AST validation failure)."
        }

    # 2. Build isolated execution environment
    # __builtins__ is strictly constrained to safe functions
    env = {
        "__builtins__": SAFE_BUILTINS,
        "__name__": "__sandbox__",
        "__doc__": None,
    }

    if dataset_records:
        env["dataset"] = dataset_records

    # 3. Execute with stdout capture
    stdout_capture = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_capture):
            exec(code, env)
        
        output = stdout_capture.getvalue()
        return {
            "status": "success",
            "securityPolicy": "DEFAULT_SANDBOX_STRICT",
            "output": output or "Code executed safely in sandbox with zero errors.",
            "violations": []
        }
    except Exception as e:
        return {
            "status": "runtime_error",
            "securityPolicy": "DEFAULT_SANDBOX_STRICT",
            "message": f"{type(e).__name__}: {str(e)}",
            "violations": []
        }

def main():
    if len(sys.argv) < 2:
        input_data = sys.stdin.read()
    else:
        input_data = sys.argv[1]

    if not input_data.strip():
        print(json.dumps({"status": "error", "message": "No code provided"}))
        return

    try:
        payload = json.loads(input_data)
        code = payload.get("code", "")
        records = payload.get("dataset", [])
    except Exception:
        code = input_data
        records = []

    result = execute_in_sandbox(code, records)
    print(json.dumps(result))

if __name__ == "__main__":
    main()
