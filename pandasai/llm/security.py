import sys
import builtins

# Define a whitelist of safe modules and functions
SAFE_MODULES = ['math', 'numpy', 'pandas']
SAFE_FUNCTIONS = ['sum', 'mean', 'median']

# Define a custom dictionary for the generated code's global namespace
global_dict = {}

# Restrict access to unsafe modules and functions
def custom_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name in SAFE_MODULES:
        return orig_import(name, globals, locals, fromlist, level)
    else:
        raise ImportError(f"Module '{name}' is not allowed")

def custom_getattr(obj, name):
    if name in SAFE_FUNCTIONS:
        return orig_getattr(obj, name)
    else:
        raise AttributeError(f"Function '{name}' is not allowed")

# Override the built-in import and getattr functions
orig_import = builtins.__import__
builtins.__import__ = custom_import
orig_getattr = builtins.getattr
builtins.getattr = custom_getattr

try:
    # Execute the generated code with the custom global namespace
    exec(llm_generated_code, global_dict)
except Exception as e:
    # In case of an exception, print the error message and the traceback
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    # Restore the original import and getattr functions
    builtins.__import__ = orig_import
    builtins.getattr = orig_getattr
