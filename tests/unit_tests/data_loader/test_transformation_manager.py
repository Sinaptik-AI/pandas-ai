from datetime import datetime

import pandas as pd
import pytest

from pandasai.data_loader.transformation_manager import TransformationManager
from pandasai.exceptions import UnsupportedTransformation


class TestTransformationManager:
    def test_anonymize_email(self):
        """Test that email anonymization preserves domain but hides username."""
        df = pd.DataFrame(
            {
                "email": [
                    "user1@example.com",
                    "user2@example.com",
                    "test.user@domain.org",
                ]
            }
        )

        manager = TransformationManager(df)
        result = manager.anonymize("email").df

        assert all(result["email"].str.contains("@"))
        assert "@example.com" in result.iloc[0]["email"]
        assert "@example.com" in result.iloc[1]["email"]
        assert "@domain.org" in result.iloc[2]["email"]
        assert not any(result["email"].isin(["user1@example.com", "user2@example.com"]))

    def test_anonymize_non_email(self):
        """Test that non-email values are completely anonymized."""
        df = pd.DataFrame({"name": ["John Doe", "Jane Smith"]})

        manager = TransformationManager(df)
        result = manager.anonymize("name").df

        assert result.iloc[0]["name"] == "*" * len("John Doe")
        assert result.iloc[1]["name"] == "*" * len("Jane Smith")

    def test_anonymize_handles_na(self):
        """Test that NA values are preserved during anonymization."""
        df = pd.DataFrame({"email": ["user@example.com", None, pd.NA]})

        manager = TransformationManager(df)
        result = manager.anonymize("email").df

        assert pd.isna(result.iloc[1]["email"])
        assert pd.isna(result.iloc[2]["email"])

    def test_convert_timezone(self):
        """Test timezone conversion."""
        df = pd.DataFrame(
            {
                "timestamp": pd.to_datetime(
                    ["2023-01-01T12:00:00+00:00", "2023-01-02T15:30:00+00:00"]
                )
            }
        )

        manager = TransformationManager(df)
        result = manager.convert_timezone("timestamp", "US/Pacific").df

        assert all(ts.tzinfo is not None for ts in result["timestamp"])
        assert all(
            ts.tzname() == "PST" or ts.tzname() == "PDT" for ts in result["timestamp"]
        )

    def test_apply_multiple_transformations(self):
        """Test applying multiple transformations in sequence."""
        df = pd.DataFrame(
            {
                "email": ["user1@example.com", "user2@example.com"],
                "timestamp": pd.to_datetime(
                    ["2023-01-01T12:00:00+00:00", "2023-01-02T15:30:00+00:00"]
                ),
            }
        )

        transformations = [
            type(
                "Transformation",
                (),
                {"type": "anonymize", "params": {"column": "email"}},
            )(),
            type(
                "Transformation",
                (),
                {
                    "type": "convert_timezone",
                    "params": {"column": "timestamp", "to": "UTC"},
                },
            )(),
        ]

        manager = TransformationManager(df)
        result = manager.apply_transformations(transformations)

        # Check anonymization
        assert all(result["email"].str.contains("@example.com"))
        assert not any(result["email"].isin(["user1@example.com", "user2@example.com"]))

        # Check timezone conversion
        assert all(ts.tzinfo is not None for ts in result["timestamp"])
        assert all(ts.tzname() == "UTC" for ts in result["timestamp"])

    def test_unsupported_transformation(self):
        """Test that unsupported transformation type raises exception."""
        df = pd.DataFrame({"col": [1, 2, 3]})

        transformations = [
            type(
                "Transformation",
                (),
                {"type": "unsupported_type", "params": {"column": "col"}},
            )()
        ]

        manager = TransformationManager(df)
        with pytest.raises(UnsupportedTransformation):
            manager.apply_transformations(transformations)
