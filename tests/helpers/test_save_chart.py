import os
import tempfile
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
            save_charts_path = os.path.join(temp_dir, "charts")
            assert not os.path.exists(save_charts_path)

            expected_code = f"""
import matplotlib.pyplot as plt
plt.plot([1, 2, 3], [4, 5, 6])
plt.savefig("{os.path.join(save_charts_path, file_name)}.png")
plt.show()
"""
            result = add_save_chart(code, logger, file_name, save_charts_path)
            assert result == expected_code
            assert os.path.exists(save_charts_path)
