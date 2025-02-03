from pandasai.helpers.sql_sanitizer import is_sql_query_safe, sanitize_sql_table_name


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

    def test_safe_select_query(self):
        query = "SELECT * FROM users WHERE username = 'admin';"
        assert is_sql_query_safe(query)

    def test_safe_with_query(self):
        query = "WITH user_data AS (SELECT * FROM users) SELECT * FROM user_data;"
        assert is_sql_query_safe(query)

    def test_unsafe_insert_query(self):
        query = "INSERT INTO users (username, password) VALUES ('admin', 'password');"
        assert not is_sql_query_safe(query)

    def test_unsafe_update_query(self):
        query = "UPDATE users SET password = 'newpassword' WHERE username = 'admin';"
        assert not is_sql_query_safe(query)

    def test_unsafe_delete_query(self):
        query = "DELETE FROM users WHERE username = 'admin';"
        assert not is_sql_query_safe(query)

    def test_unsafe_drop_query(self):
        query = "DROP TABLE users;"
        assert not is_sql_query_safe(query)

    def test_unsafe_alter_query(self):
        query = "ALTER TABLE users ADD COLUMN age INT;"
        assert not is_sql_query_safe(query)

    def test_unsafe_create_query(self):
        query = "CREATE TABLE users (id INT, username VARCHAR(50));"
        assert not is_sql_query_safe(query)

    def test_safe_select_with_comment(self):
        query = "SELECT * FROM users WHERE username = 'admin' -- comment"
        assert not is_sql_query_safe(query)  # Blocked by comment detection

    def test_safe_select_with_inline_comment(self):
        query = "SELECT * FROM users /* inline comment */ WHERE username = 'admin';"
        assert not is_sql_query_safe(query)  # Blocked by comment detection

    def test_unsafe_query_with_subquery(self):
        query = "SELECT * FROM users WHERE id IN (SELECT user_id FROM orders);"
        assert is_sql_query_safe(query)  # No dangerous keyword in main or subquery

    def test_unsafe_query_with_subquery_insert(self):
        query = (
            "SELECT * FROM users WHERE id IN (INSERT INTO orders (user_id) VALUES (1));"
        )
        assert not is_sql_query_safe(query)  # Subquery contains INSERT, blocked

    def test_invalid_sql(self):
        query = "INVALID SQL QUERY"
        assert not is_sql_query_safe(query)  # Invalid query should return False

    def test_safe_query_with_multiple_keywords(self):
        query = "SELECT name FROM users WHERE username = 'admin' AND age > 30;"
        assert is_sql_query_safe(query)  # Safe query with no dangerous keyword

    def test_safe_query_with_subquery(self):
        query = "SELECT name FROM users WHERE username IN (SELECT username FROM users WHERE age > 30);"
        assert is_sql_query_safe(
            query
        )  # Safe query with subquery, no dangerous keyword

    def test_safe_query_with_query_params(self):
        query = "SELECT * FROM (SELECT * FROM heart_data) AS filtered_data LIMIT %s OFFSET %s"
        assert is_sql_query_safe(query)


if __name__ == "__main__":
    unittest.main()
