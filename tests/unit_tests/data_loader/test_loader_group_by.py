import pandas as pd
import pytest

from pandasai.data_loader.loader import DatasetLoader
from pandasai.data_loader.semantic_layer_schema import (
    Column,
    SemanticLayerSchema,
    Source,
)


class TestLoaderGroupBy:
    def test_simple_group_by_with_aggregation(self):
        """Test simple group by with count and average aggregations"""
        df = pd.DataFrame(
            {"category": ["A", "A", "B", "B", "B"], "value": [10, 20, 30, 40, 50]}
        )

        schema = SemanticLayerSchema(
            name="test",
            source=Source(type="parquet", path="test.parquet"),
            columns=[
                Column(name="category", type="string"),
                Column(name="avg_value", type="float", expression="avg(value)"),
                Column(name="count", type="integer", expression="count(*)"),
            ],
            group_by=["category"],
        )

        loader = DatasetLoader()
        loader.schema = schema

        result = loader._apply_group_by(df)

        expected = pd.DataFrame(
            {"category": ["A", "B"], "avg_value": [15.0, 40.0], "count": [2, 3]}
        )

        pd.testing.assert_frame_equal(
            result.reset_index(drop=True), expected.reset_index(drop=True)
        )

    def test_group_by_with_case_expression(self):
        """Test group by with CASE expression and aggregations"""
        df = pd.DataFrame(
            {"age": [25, 35, 45, 55, 65], "value": [100, 200, 300, 400, 500]}
        )

        schema = SemanticLayerSchema(
            name="test",
            source=Source(type="parquet", path="test.parquet"),
            columns=[
                Column(
                    name="age_group",
                    type="string",
                    expression="case when age < 30 then 'Young' when age < 50 then 'Middle' else 'Senior' end",
                ),
                Column(name="avg_value", type="float", expression="avg(value)"),
                Column(name="count", type="integer", expression="count(*)"),
            ],
            group_by=["age_group"],
        )

        loader = DatasetLoader()
        loader.schema = schema

        result = loader._apply_group_by(df)

        expected = pd.DataFrame(
            {
                "age_group": ["Young", "Middle", "Senior"],
                "avg_value": [100.0, 250.0, 450.0],
                "count": [1, 2, 2],
            }
        )

        pd.testing.assert_frame_equal(
            result.reset_index(drop=True), expected.reset_index(drop=True)
        )

    def test_multiple_group_by_columns(self):
        """Test grouping by multiple columns with aggregations"""
        df = pd.DataFrame(
            {
                "category": ["A", "A", "B", "B", "B"],
                "subcategory": ["X", "Y", "X", "X", "Y"],
                "value": [10, 20, 30, 40, 50],
            }
        )

        schema = SemanticLayerSchema(
            name="test",
            source=Source(type="parquet", path="test.parquet"),
            columns=[
                Column(name="category", type="string"),
                Column(name="subcategory", type="string"),
                Column(name="avg_value", type="float", expression="avg(value)"),
                Column(name="count", type="integer", expression="count(*)"),
            ],
            group_by=["category", "subcategory"],
        )

        loader = DatasetLoader()
        loader.schema = schema

        result = loader._apply_group_by(df)

        expected = pd.DataFrame(
            {
                "category": ["A", "A", "B", "B"],
                "subcategory": ["X", "Y", "X", "Y"],
                "avg_value": [10.0, 20.0, 35.0, 50.0],
                "count": [1, 1, 2, 1],
            }
        )

        pd.testing.assert_frame_equal(
            result.reset_index(drop=True), expected.reset_index(drop=True)
        )

    def test_no_group_by(self):
        """Test that DataFrame is unchanged when no group by is specified"""
        df = pd.DataFrame({"category": ["A", "B", "C"], "value": [10, 20, 30]})

        schema = SemanticLayerSchema(
            name="test",
            source=Source(type="parquet", path="test.parquet"),
            columns=[
                Column(name="category", type="string"),
                Column(name="value", type="integer"),
            ],
        )

        loader = DatasetLoader()
        loader.schema = schema

        result = loader._apply_group_by(df)

        pd.testing.assert_frame_equal(result, df)

    def test_group_by_with_null_values(self):
        """Test group by handling of null values"""
        df = pd.DataFrame(
            {"category": ["A", "A", None, "B", None], "value": [10, 20, 30, 40, 50]}
        )

        schema = SemanticLayerSchema(
            name="test",
            source=Source(type="parquet", path="test.parquet"),
            columns=[
                Column(name="category", type="string"),
                Column(name="avg_value", type="float", expression="avg(value)"),
                Column(name="count", type="integer", expression="count(*)"),
            ],
            group_by=["category"],
        )

        loader = DatasetLoader()
        loader.schema = schema

        result = loader._apply_group_by(df)

        expected = pd.DataFrame(
            {
                "category": ["A", "B", None],
                "avg_value": [15.0, 40.0, 40.0],
                "count": [2, 1, 2],
            }
        )

        pd.testing.assert_frame_equal(
            result.reset_index(drop=True), expected.reset_index(drop=True)
        )
