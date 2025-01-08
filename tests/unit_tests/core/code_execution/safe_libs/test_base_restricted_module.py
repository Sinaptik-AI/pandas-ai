import unittest
from pandasai.core.code_execution.safe_libs.base_restricted_module import (
    BaseRestrictedModule,
    SecurityError,
)


class TestBaseRestrictedModule(unittest.TestCase):
    def setUp(self):
        """Set up the test environment for BaseRestrictedModule."""
        self.module = BaseRestrictedModule()

    def test_wrap_function_allows_safe_arguments(self):
        """Test that the wrapped function allows safe arguments."""

        @self.module._wrap_function
        def safe_function(arg1, arg2):
            return arg1 + arg2

        result = safe_function(1, 2)
        self.assertEqual(result, 3)

    def test_wrap_function_rejects_restricted_module(self):
        """Test that the wrapped function rejects a restricted module as an argument."""

        @self.module._wrap_function
        def function_with_restriction(arg):
            return arg

        with self.assertRaises(SecurityError) as context:
            function_with_restriction("os")

        self.assertEqual(
            str(context.exception), "Potential security risk: 'os' is not allowed"
        )

    def test_wrap_function_rejects_restricted_module_in_kwargs(self):
        """Test that the wrapped function rejects a restricted module in keyword arguments."""

        @self.module._wrap_function
        def function_with_restriction(arg):
            return arg

        with self.assertRaises(SecurityError) as context:
            function_with_restriction(arg="sys")

        self.assertEqual(
            str(context.exception), "Potential security risk: 'sys' is not allowed"
        )

    def test_wrap_class_allows_safe_method(self):
        """Test that the wrapped class allows safe method calls."""

        class SafeClass:
            def safe_method(self, arg1, arg2):
                return arg1 + arg2

        WrappedSafeClass = self.module._wrap_class(SafeClass)
        instance = WrappedSafeClass()

        # Access the method through the wrapped instance
        result = instance.safe_method(1, 2)
        self.assertEqual(result, 3)

    def test_wrap_class_rejects_restricted_method(self):
        """Test that the wrapped class rejects a restricted method call."""

        class RestrictedClass:
            def restricted_method(self, arg):
                return arg

        WrappedRestrictedClass = self.module._wrap_class(RestrictedClass)
        instance = WrappedRestrictedClass()

        with self.assertRaises(SecurityError) as context:
            instance.restricted_method("importlib")

        self.assertEqual(
            str(context.exception),
            "Potential security risk: 'importlib' is not allowed",
        )

    def test_wrap_function_with_multiple_arguments(self):
        """Test that the wrapped function allows multiple safe arguments."""

        @self.module._wrap_function
        def multi_arg_function(arg1, arg2, arg3):
            return arg1 * arg2 + arg3

        result = multi_arg_function(2, 3, 4)
        self.assertEqual(result, 10)

    def test_wrap_function_with_list_argument(self):
        """Test that the wrapped function allows a list as an argument."""

        @self.module._wrap_function
        def list_function(my_list):
            return sum(my_list)

        result = list_function([1, 2, 3])
        self.assertEqual(result, 6)

    def test_wrap_function_with_dict_argument(self):
        """Test that the wrapped function allows a dictionary as an argument."""

        @self.module._wrap_function
        def dict_function(my_dict):
            return my_dict.get("key", 0)

        result = dict_function({"key": 10})
        self.assertEqual(result, 10)

    def test_wrap_class_with_inherited_methods(self):
        """Test that the wrapped class allows inherited method calls."""

        class BaseClass:
            def base_method(self):
                return "Base method called"

        class DerivedClass(BaseClass):
            def derived_method(self):
                return "Derived method called"

        WrappedDerivedClass = self.module._wrap_class(DerivedClass)
        instance = WrappedDerivedClass()
        self.assertEqual(instance.base_method(), "Base method called")
        self.assertEqual(instance.derived_method(), "Derived method called")

    def test_wrap_function_with_restricted_module_in_args(self):
        """Test that the wrapped function rejects a restricted module in arguments."""

        @self.module._wrap_function
        def function_with_restriction(arg):
            return arg

        with self.assertRaises(SecurityError) as context:
            function_with_restriction("subprocess")

        self.assertEqual(
            str(context.exception),
            "Potential security risk: 'subprocess' is not allowed",
        )


if __name__ == "__main__":
    unittest.main()
