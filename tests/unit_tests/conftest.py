import os
import statistics
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pandasai import find_project_root


@pytest.fixture(scope="session")
def mock_json_load():
    mock = MagicMock()

    with patch("json.load", mock):
        yield mock


def pytest_terminal_summary(terminalreporter, exitstatus):
    scores_file = Path(find_project_root()) / "test_agent_llm_judge.txt"

    if os.path.exists(scores_file):
        with open(scores_file, "r") as file:
            score_line = file.readline().strip()

            # Ensure the line is a valid number
            if score_line.replace(".", "", 1).isdigit():
                avg_score = float(score_line)
                terminalreporter.write(f"\n--- Evaluation Score Summary ---\n")
                terminalreporter.write(f"Average Score: {avg_score:.2f}\n")

        os.remove(scores_file)
