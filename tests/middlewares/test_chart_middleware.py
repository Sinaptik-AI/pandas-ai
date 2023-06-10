"""Unit tests for the charts middleware class"""

from pandasai.middlewares.charts import ChartsMiddleware


class TestChartsMiddleware:
    """Unit tests for the charts middleware class"""

    def test_add_close_all(self):
        """Test adding plt.close('all') to the code"""
        code = "plt.show()"
        middleware = ChartsMiddleware()
        assert middleware(code=code) == "plt.show()\nplt.close('all')"

    def test_not_add_close_all_if_already_there(self):
        """Test that plt.close('all') is not added if it is already there"""
        code = "plt.show()\nplt.close('all')"
        middleware = ChartsMiddleware()
        assert middleware(code=code) == "plt.show()\nplt.close('all')"

    def test_no_add_close_all_if_not_show(self):
        """Test that plt.close('all') is not added if plt.show() is not there"""
        code = "plt.plot()"
        middleware = ChartsMiddleware()
        assert middleware(code=code) == "plt.plot()"
