import os
import re


def sanitize_sql_table_name(filepath: str) -> str:
    # Extract the file name without extension
    file_name = os.path.splitext(os.path.basename(filepath))[0]

    # Replace invalid characters with underscores
    sanitized_name = re.sub(r"[^a-zA-Z0-9_]", "_", file_name)

    # Truncate to a reasonable length (e.g., 64 characters)
    max_length = 64
    sanitized_name = sanitized_name[:max_length]

    return sanitized_name
