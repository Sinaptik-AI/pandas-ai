from datetime import datetime

import numpy as np
import pandas as pd
import pytest

from pandasai.data_loader.semantic_layer_schema import (
    Transformation,
    TransformationParams,
)
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
        assert all(ts.tzname() == "PST" for ts in result["timestamp"])

    def test_to_lowercase(self):
        """Test converting strings to lowercase."""
        df = pd.DataFrame({"text": ["Hello WORLD", "PyThOn", "TEST"]})

        manager = TransformationManager(df)
        result = manager.to_lowercase("text").df

        assert all(result["text"] == ["hello world", "python", "test"])

    def test_to_uppercase(self):
        """Test converting strings to uppercase."""
        df = pd.DataFrame({"text": ["Hello World", "Python", "test"]})

        manager = TransformationManager(df)
        result = manager.to_uppercase("text").df

        assert all(result["text"] == ["HELLO WORLD", "PYTHON", "TEST"])

    def test_strip(self):
        """Test stripping whitespace."""
        df = pd.DataFrame({"text": [" hello ", "  world  ", "python\n"]})

        manager = TransformationManager(df)
        result = manager.strip("text").df

        assert all(result["text"] == ["hello", "world", "python"])

    def test_round_numbers(self):
        """Test rounding numbers."""
        df = pd.DataFrame({"numbers": [1.23456, 2.78901, 3.5]})

        manager = TransformationManager(df)
        result = manager.round_numbers("numbers", 2).df

        assert all(result["numbers"] == [1.23, 2.79, 3.50])

    def test_scale(self):
        """Test scaling numbers."""
        df = pd.DataFrame({"numbers": [1, 2, 3]})

        manager = TransformationManager(df)
        result = manager.scale("numbers", 2.5).df

        assert all(result["numbers"] == [2.5, 5.0, 7.5])

    def test_format_date(self):
        """Test date formatting."""
        df = pd.DataFrame({"date": pd.to_datetime(["2023-01-01", "2023-12-31"])})

        manager = TransformationManager(df)
        result = manager.format_date("date", "%d/%m/%Y").df

        assert all(result["date"] == ["01/01/2023", "31/12/2023"])

    def test_to_numeric(self):
        """Test converting to numeric."""
        df = pd.DataFrame({"mixed": ["1", "2.5", "invalid", "3"]})

        manager = TransformationManager(df)
        result = manager.to_numeric("mixed").df

        assert result["mixed"].dtype == np.float64
        assert pd.isna(result.iloc[2]["mixed"])
        assert result.iloc[3]["mixed"] == 3.0

    def test_to_datetime(self):
        """Test converting to datetime."""
        df = pd.DataFrame({"dates": ["2023-01-01", "2023-12-31", "invalid"]})

        manager = TransformationManager(df)
        result = manager.to_datetime("dates").df

        assert pd.api.types.is_datetime64_any_dtype(result["dates"])
        assert pd.isna(result.iloc[2]["dates"])

    def test_fill_na(self):
        """Test filling NA values."""
        df = pd.DataFrame({"values": [1, None, pd.NA, 4]})

        manager = TransformationManager(df)
        result = manager.fill_na("values", 0).df

        assert all(result["values"] == [1, 0, 0, 4])

    def test_method_chaining(self):
        """Test that methods can be chained."""
        df = pd.DataFrame(
            {"text": [" Hello ", " World "], "numbers": [1.23456, 2.78901]}
        )

        manager = TransformationManager(df)
        result = (
            manager.strip("text").to_uppercase("text").round_numbers("numbers", 2).df
        )

        assert all(result["text"] == ["HELLO", "WORLD"])
        assert all(result["numbers"] == [1.23, 2.79])

    def test_apply_transformations(self):
        """Test applying multiple transformations through configuration."""
        df = pd.DataFrame(
            {
                "email": ["user1@example.com", "user2@example.com"],
                "timestamp": pd.to_datetime(
                    ["2023-01-01T12:00:00+00:00", "2023-01-02T15:30:00+00:00"]
                ),
                "text": [" Hello ", " World "],
                "numbers": [1.23456, 2.78901],
            }
        )

        transformations = [
            Transformation(
                type="anonymize",
                params=TransformationParams(column="email"),
            ),
            Transformation(
                type="convert_timezone",
                params=TransformationParams(column="timestamp", to="UTC"),
            ),
            Transformation(
                type="strip",
                params=TransformationParams(column="text"),
            ),
            Transformation(
                type="round_numbers",
                params=TransformationParams(column="numbers", decimals=2),
            ),
        ]

        manager = TransformationManager(df)
        result = manager.apply_transformations(transformations)

        # Check anonymization
        assert all(result["email"].str.contains("@example.com"))
        assert not any(result["email"].isin(["user1@example.com", "user2@example.com"]))

        # Check timezone conversion
        assert all(ts.tzinfo is not None for ts in result["timestamp"])
        assert all(ts.tzname() == "UTC" for ts in result["timestamp"])

        # Check strip
        assert all(result["text"] == ["Hello", "World"])

        # Check rounding
        assert all(result["numbers"] == [1.23, 2.79])

    def test_unsupported_transformation(self):
        """Test that unsupported transformation type raises exception."""
        df = pd.DataFrame({"col": [1, 2, 3]})

        # Test that invalid transformation type is caught by model validation
        with pytest.raises(ValueError, match="Unsupported transformation type"):
            Transformation(
                type="non_existent_type",  # This is an invalid type
                params=TransformationParams(column="col"),
            )

        # Test that missing handler is caught by transformation manager
        transformations = [
            Transformation(
                type="to_lowercase",  # This is a valid type
                params=TransformationParams(column="col"),
            )
        ]

        manager = TransformationManager(df)
        # Override the transformation handlers to make it raise the error
        manager.transformation_handlers = {}

        with pytest.raises(UnsupportedTransformation):
            manager.apply_transformations(transformations)

    def test_replace(self):
        """Test replacing text."""
        df = pd.DataFrame({"text": ["hello world", "world hello", "hello hello"]})

        manager = TransformationManager(df)
        result = manager.replace("text", "hello", "hi").df

        assert all(result["text"] == ["hi world", "world hi", "hi hi"])

    def test_extract(self):
        """Test extracting text with regex."""
        df = pd.DataFrame({"text": ["user123@example.com", "test456@domain.org"]})

        manager = TransformationManager(df)
        result = manager.extract("text", r"(\d+)").df

        assert all(result["text"] == ["123", "456"])

    def test_truncate(self):
        """Test string truncation."""
        df = pd.DataFrame({"text": ["very long text", "short", "another long text"]})

        manager = TransformationManager(df)
        result = manager.truncate("text", 8, add_ellipsis=True).df

        assert result["text"].tolist() == ["very...", "short", "anoth..."]

    def test_pad(self):
        """Test string padding."""
        df = pd.DataFrame({"text": ["123", "4567", "89"]})

        manager = TransformationManager(df)
        result = manager.pad("text", width=5, side="left", pad_char="0").df

        assert all(result["text"] == ["00123", "04567", "00089"])

    def test_clip(self):
        """Test clipping numeric values."""
        df = pd.DataFrame({"numbers": [1, 5, 10, 15, 20]})

        manager = TransformationManager(df)
        result = manager.clip("numbers", lower=5, upper=15).df

        assert all(result["numbers"] == [5, 5, 10, 15, 15])

    def test_bin(self):
        """Test binning continuous data."""
        df = pd.DataFrame({"numbers": [1, 5, 10, 15, 20]})

        manager = TransformationManager(df)
        result = manager.bin("numbers", bins=[0, 10, 20], labels=["low", "high"]).df

        assert result["numbers"].tolist() == ["low", "low", "low", "high", "high"]

    def test_normalize(self):
        """Test min-max normalization."""
        df = pd.DataFrame({"numbers": [1, 3, 5]})

        manager = TransformationManager(df)
        result = manager.normalize("numbers").df

        assert result["numbers"].tolist() == [0.0, 0.5, 1.0]

    def test_standardize(self):
        """Test z-score standardization."""
        df = pd.DataFrame({"numbers": [1, 2, 3]})

        manager = TransformationManager(df)
        result = manager.standardize("numbers").df

        # Mean should be 0 and std should be 1
        assert abs(result["numbers"].mean()) < 1e-10
        assert abs(result["numbers"].std() - 1) < 1e-10

    def test_map_values(self):
        """Test mapping values."""
        df = pd.DataFrame({"categories": ["A", "B", "C", "A"]})

        mapping = {"A": "Category A", "B": "Category B", "C": "Category C"}
        manager = TransformationManager(df)
        result = manager.map_values("categories", mapping).df

        assert all(
            result["categories"]
            == ["Category A", "Category B", "Category C", "Category A"]
        )

    def test_encode_categorical(self):
        """Test one-hot encoding."""
        df = pd.DataFrame({"categories": ["A", "B", "A", "C"]})

        manager = TransformationManager(df)
        result = manager.encode_categorical("categories", drop_first=True).df

        # Should have n-1 columns for n categories when drop_first=True
        assert "categories_B" in result.columns
        assert "categories_C" in result.columns
        assert "categories_A" not in result.columns
        assert result.shape[1] == 2

    def test_complex_transformation_chain(self):
        """Test a complex chain of transformations."""
        df = pd.DataFrame(
            {
                "text": [" Hello World ", "Python  ", " Data Science "],
                "numbers": [1.23456, -5.6789, 10.0],
                "categories": ["A", "B", "A"],
            }
        )

        manager = TransformationManager(df)
        result = (
            manager.strip("text")
            .to_uppercase("text")
            .truncate("text", 8)
            .clip("numbers", lower=0, upper=None)
            .round_numbers("numbers", 2)
            .encode_categorical("categories")
            .df
        )

        assert result["text"].tolist() == ["HELLO...", "PYTHON", "DATA..."]
        assert result["numbers"].tolist() == [1.23, 0.00, 10.00]
        assert "categories_B" in result.columns

    def test_validate_email(self):
        """Test email validation."""
        df = pd.DataFrame(
            {"email": ["user@example.com", "invalid.email", "another@domain.com", None]}
        )

        manager = TransformationManager(df)
        result = manager.validate_email("email").df

        assert result["email_valid"].tolist() == [True, False, True, False]

        result = manager.validate_email("email", drop_invalid=True).df
        assert len(result) == 2
        assert all(result["email"].isin(["user@example.com", "another@domain.com"]))

    def test_validate_date_range(self):
        """Test date range validation."""
        df = pd.DataFrame(
            {"date": ["2023-01-01", "2024-06-15", "2025-12-31", "invalid", None]}
        )

        manager = TransformationManager(df)
        result = manager.validate_date_range("date", "2023-01-01", "2024-12-31").df

        assert result["date_valid"].tolist() == [True, True, False, False, False]

        result = manager.validate_date_range(
            "date", "2023-01-01", "2024-12-31", drop_invalid=True
        ).df
        assert len(result) == 2
        assert all(result["date"].isin(["2023-01-01", "2024-06-15"]))

    def test_normalize_phone(self):
        """Test phone number normalization."""
        df = pd.DataFrame(
            {"phone": ["1234567890", "(123) 456-7890", "+44 20 7123 4567", None]}
        )

        manager = TransformationManager(df)
        result = manager.normalize_phone("phone").df

        expected = ["+1-123-456-7890", "+1-123-456-7890", "+44-207-123-4567", None]
        assert result["phone"].tolist() == expected

    def test_remove_duplicates(self):
        """Test duplicate removal."""
        df = pd.DataFrame({"id": [1, 2, 1, 3], "value": ["a", "b", "a", "c"]})

        manager = TransformationManager(df)
        result = manager.remove_duplicates("id").df

        assert len(result) == 3
        assert result["id"].tolist() == [1, 2, 3]

    def test_validate_foreign_key(self):
        """Test foreign key validation."""
        users_df = pd.DataFrame({"user_id": [1, 2, 3]})

        orders_df = pd.DataFrame({"order_id": [1, 2, 3, 4], "user_id": [1, 2, 4, None]})

        manager = TransformationManager(orders_df)
        result = manager.validate_foreign_key("user_id", users_df, "user_id").df

        assert result["user_id_valid"].tolist() == [True, True, False, False]

        result = manager.validate_foreign_key(
            "user_id", users_df, "user_id", drop_invalid=True
        ).df
        assert len(result) == 2
        assert all(result["user_id"].isin([1, 2]))

    def test_ensure_positive(self):
        """Test ensuring positive values."""
        df = pd.DataFrame({"amount": [100, -50, 0, 75, -25]})

        manager = TransformationManager(df)
        result = manager.ensure_positive("amount").df
        assert result["amount"].tolist() == [100, 0, 0, 75, 0]

        # Create a new manager to start fresh
        manager = TransformationManager(df)
        result = manager.ensure_positive("amount", drop_negative=True).df
        assert len(result) == 3
        assert result["amount"].tolist() == [100, 0, 75]

    def test_standardize_categories(self):
        """Test category standardization."""
        df = pd.DataFrame(
            {"company": ["Apple Inc.", "Apple Computer", "Microsoft Corp", "MS"]}
        )

        mapping = {
            "Apple Inc.": "Apple",
            "Apple Computer": "Apple",
            "Microsoft Corp": "Microsoft",
            "MS": "Microsoft",
        }

        manager = TransformationManager(df)
        result = manager.standardize_categories("company", mapping).df

        expected = ["Apple", "Apple", "Microsoft", "Microsoft"]
        assert result["company"].tolist() == expected
