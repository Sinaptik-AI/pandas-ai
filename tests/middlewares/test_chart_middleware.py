"""Unit tests for the charts middleware class"""

from pandasai.middlewares.charts import ChartsMiddleware
from unittest.mock import Mock

import pytest


class TestChartsMiddleware:
    """Unit tests for the charts middleware class"""

    @pytest.fixture
    def middleware(self):
        return ChartsMiddleware()

    def test_add_close_all(self, middleware):
        """Test adding plt.close('all') to the code"""
        code = "plt.show()"
        assert middleware(code=code) == "plt.show(block=False)\nplt.close('all')"

    def test_add_close_all_if_in_console(self, middleware):
        """
        Test should not add block=False if running in console
        """
        middleware._is_running_in_console = Mock(return_value=True)
        code = "plt.show()"
        assert middleware(code=code) == "plt.show()\nplt.close('all')"

    def test_not_add_close_all_if_already_there(self, middleware):
        """Test that plt.close('all') is not added if it is already there"""
        code = "plt.show()\nplt.close('all')"
        assert middleware(code=code) == "plt.show(block=False)\nplt.close('all')"

    def test_no_add_close_all_if_not_show(self, middleware):
        """Test that plt.close('all') is not added if plt.show() is not there"""
        code = "plt.plot()"
        assert middleware(code=code) == "plt.plot()"
