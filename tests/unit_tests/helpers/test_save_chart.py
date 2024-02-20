import os
import tempfile
from pathlib import Path

from pandasai.helpers.logger import Logger
from pandasai.helpers.save_chart import add_save_chart


class TestAddSaveChart:
    def test_add_save_chart_with_default_path(self):
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig("temp_chart.png")
plt.show()
"""
        logger = Logger()
        file_name = "test_chart"
        expected_code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig("temp_chart.png")
plt.show()
"""
        result = add_save_chart(code, logger, file_name)
        assert result == expected_code

    def test_add_save_chart_with_user_defined_path(self):
        code = """
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig("temp_chart.png")
plt.show()
"""
        logger = Logger()
        file_name = "temp_chart"

        with tempfile.TemporaryDirectory() as temp_dir:
            save_charts_path = Path(temp_dir) / "charts"
            assert not save_charts_path.exists()
            full_path_to_file = save_charts_path / f"{file_name}.png"

            expected_code = f"""
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig("{full_path_to_file.as_posix()}")
plt.show()
"""
            result = add_save_chart(code, logger, file_name, save_charts_path)
            assert result == expected_code
            assert os.path.exists(save_charts_path)
