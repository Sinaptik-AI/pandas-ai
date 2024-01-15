import re


def extract_table_names(sql_query):
    # Regular expression pattern to match table names in FROM and JOIN clauses
    pattern = r"\bFROM\s+(\S+)\b|\bJOIN\s+(\S+)\b"

    # Find all matches in the SQL query
    matches = re.findall(pattern, sql_query, re.IGNORECASE)

    # Flatten the list of matches and filter out empty strings
    return [table_name for match in matches for table_name in match if table_name]
