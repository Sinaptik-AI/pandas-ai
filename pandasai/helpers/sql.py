import re


def extract_table_names(sql_query):
    # Regular expression pattern to match table names in FROM and JOIN clauses
    pattern = r"(?:FROM|JOIN)\s+(?<!:)(\"?\w+\"?)(?=\s|$)"

    # Find all matches in the SQL query
    matches = re.findall(pattern, sql_query, re.IGNORECASE)
    return matches
