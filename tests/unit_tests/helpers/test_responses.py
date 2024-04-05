import unittest

from PIL import Image

from pandasai.helpers.logger import Logger
from pandasai.llm.fake import FakeLLM
from pandasai.responses.context import Context
from pandasai.responses.response_parser import ResponseParser
from pandasai.schemas.df_config import Config


class TestFormatPlot(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        llm = FakeLLM(output=None)
        config = {"llm": llm, "enable_cache": True}
        config = Config(**config)
        context = Context(config=config, logger=Logger())
        cls.response_parser = ResponseParser(context)

    def test_display_plot_from_file(self):
        result = {"type": "plot", "value": "path/to/plot.png"}
        with unittest.mock.patch(
            "builtins.open", unittest.mock.mock_open(read_data=b"")
        ):
            with unittest.mock.patch(
                "PIL.Image.open", return_value=Image.new("RGB", (100, 100))
            ):
                with unittest.mock.patch("PIL.Image.Image.show") as mock_show:
                    self.assertEqual(
                        self.response_parser.format_plot(result), "path/to/plot.png"
                    )
                    mock_show.assert_called_once()

    def test_display_plot_from_bytes(self):
        result = {"type": "plot", "value": b"fake_image_data"}
        with unittest.mock.patch(
            "PIL.Image.open", return_value=Image.new("RGB", (100, 100))
        ):
            with unittest.mock.patch("PIL.Image.Image.show"):
                self.assertEqual(
                    self.response_parser.format_plot(result), b"fake_image_data"
                )

    def test_return_value_without_display(self):
        result = {"type": "plot", "value": "path/to/plot.png"}
        with unittest.mock.patch(
            "builtins.open", unittest.mock.mock_open(read_data=b"")
        ):
            with unittest.mock.patch(
                "PIL.Image.open", return_value=Image.new("RGB", (100, 100))
            ):
                with unittest.mock.patch.object(
                    self.response_parser._context.config, "open_charts", False
                ):
                    self.assertEqual(
                        self.response_parser.format_plot(result), "path/to/plot.png"
                    )
