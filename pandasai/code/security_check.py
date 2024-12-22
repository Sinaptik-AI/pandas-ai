import ast

FORBIDDEN_BUILTIN_NAMES = ('chr', 'eval', 'exec', 'compile', 'open', '__import__')
FORBIDDEN_IMPORT_NAMES = ('os', 'io', 'base64', 'importlib')


def check_malicious_keywords_in_code(code):
    parsed_code = ast.parse(code)
    for block in ast.walk(parsed_code):
        if isinstance(block, ast.Import):
            for name in [sb for name in block.names for sb in name.name.split('.')]:
                if name in FORBIDDEN_IMPORT_NAMES:
                    return True, block
        elif isinstance(block, ast.ImportFrom):
            if block.module in FORBIDDEN_IMPORT_NAMES:
                return True, block
            for name in [sb for name in block.names for sb in name.name.split('.')]:
                if name in FORBIDDEN_IMPORT_NAMES:
                    return True, block
        elif isinstance(block, ast.Name):
            if block.id in FORBIDDEN_BUILTIN_NAMES or block.id in FORBIDDEN_IMPORT_NAMES:
                return True, block
        elif isinstance(block, ast.Attribute):
            if block.attr in FORBIDDEN_BUILTIN_NAMES:
                return True, block
    return False, None
