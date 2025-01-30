import os
import statistics
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pandasai import DataFrame, find_project_root
from pandasai.data_loader.semantic_layer_schema import SemanticLayerSchema


@pytest.fixture
def sample_dict_data():
    return {"A": [1, 2, 3], "B": [4, 5, 6]}


@pytest.fixture
def sample_df(sample_dict_data):
    return DataFrame(sample_dict_data)


@pytest.fixture
def sample_dataframes():
    df1 = DataFrame({"A": [1, 2, 3], "B": ["a", "b", "c"]})
    df2 = DataFrame({"X": [10, 20, 30], "Y": ["x", "y", "z"]})
    return [df1, df2]


@pytest.fixture
def raw_sample_schema():
    return {
        "name": "Users",
        "update_frequency": "weekly",
        "columns": [
            {
                "name": "email",
                "type": "string",
                "description": "User's email address",
            },
            {
                "name": "first_name",
                "type": "string",
                "description": "User's first name",
            },
            {
                "name": "timestamp",
                "type": "datetime",
                "description": "Timestamp of the record",
            },
        ],
        "order_by": ["created_at DESC"],
        "limit": 100,
        "transformations": [
            {"type": "anonymize", "params": {"column": "email"}},
            {
                "type": "convert_timezone",
                "params": {"column": "timestamp", "to": "UTC"},
            },
        ],
        "source": {"type": "csv", "path": "users.csv", "table": "users"},
    }


@pytest.fixture
def raw_mysql_schema():
    return {
        "name": "users",
        "update_frequency": "weekly",
        "columns": [
            {
                "name": "email",
                "type": "string",
                "description": "User's email address",
            },
            {
                "name": "first_name",
                "type": "string",
                "description": "User's first name",
            },
            {
                "name": "timestamp",
                "type": "datetime",
                "description": "Timestamp of the record",
            },
        ],
        "order_by": ["created_at DESC"],
        "limit": 100,
        "transformations": [
            {"type": "anonymize", "params": {"column": "email"}},
            {
                "type": "convert_timezone",
                "params": {"column": "timestamp", "to": "UTC"},
            },
        ],
        "source": {
            "type": "mysql",
            "connection": {
                "host": "localhost",
                "port": 3306,
                "database": "test_db",
                "user": "test_user",
                "password": "test_password",
            },
            "table": "users",
        },
    }


@pytest.fixture
def raw_mysql_view_schema():
    return {
        "name": "parent-children",
        "columns": [
            {"name": "parents.id"},
            {"name": "parents.name"},
            {"name": "children.name"},
        ],
        "relations": [{"from": "parents.id", "to": "children.id"}],
        "view": "true",
    }


@pytest.fixture
def sample_schema(raw_sample_schema):
    return SemanticLayerSchema(**raw_sample_schema)


@pytest.fixture
def mysql_schema(raw_mysql_schema):
    return SemanticLayerSchema(**raw_mysql_schema)


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
