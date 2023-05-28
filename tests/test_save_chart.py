"""Unit tests for the save_chart module."""
from datetime import datetime

from pandasai.helpers.save_chart import add_save_chart


class TestSaveChart:
    """Unit tests for the save_chart module."""

    def test_save_chart(self):
        chart_code = """
    import matplotlib.pyplot as plt
    import pandas as pd
    df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
    df.plot()
    plt.show()
    """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        export_path = f"exports/charts/plot_{timestamp}.png"
        output = add_save_chart(chart_code).split("\n")
        assert len(output) == 6
        assert output[-2] == f"plt.savefig('{export_path}')"

    def test_save_multiple_charts(self):
        chart_code = """
    import matplotlib.pyplot as plt
    import pandas as pd
    df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
    df.plot('a')
    plt.show()
    df.plot('b')
    plt.show()
    """
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        export_path = f"exports/charts/plot_{timestamp}.png"
        output = add_save_chart(chart_code).split("\n")
        assert len(output) == 9
        assert output[-5] == f"plt.savefig('{export_path}a')"
        assert output[-2] == f"plt.savefig('{export_path}b')"
