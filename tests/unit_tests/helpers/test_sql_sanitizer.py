from pandasai.helpers.sql_sanitizer import sanitize_sql_table_name


class TestSqlSanitizer:
    def test_valid_filename(self):
        filepath = "/path/to/valid_table.csv"
        expected = "valid_table"
        assert sanitize_sql_table_name(filepath) == expected

    def test_filename_with_special_characters(self):
        filepath = "/path/to/invalid!@#.csv"
        expected = "invalid___"
        assert sanitize_sql_table_name(filepath) == expected

    def test_filename_with_long_name(self):
        """Test with a filename exceeding the length limit."""
        filepath = "/path/to/" + "a" * 100 + ".csv"
        expected = "a" * 64
        assert sanitize_sql_table_name(filepath) == expected
