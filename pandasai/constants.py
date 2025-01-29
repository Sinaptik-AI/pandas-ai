"""
Constants used in the pandasai package.
"""

# Default API url
DEFAULT_API_URL = "https://api.pandabi.ai"

# Default directory to store chart if user doesn't provide any
DEFAULT_CHART_DIRECTORY = "exports/charts"

# Default directory for cache
DEFAULT_CACHE_DIRECTORY = "cache"

# Default permissions for files and directories
DEFAULT_FILE_PERMISSIONS = 0o755

# Token needed to invalidate the cache after breaking changes
CACHE_TOKEN = "pandasai1"

PANDABI_SETUP_MESSAGE = (
    "The api_key client option must be set either by passing api_key to the client "
    "or by setting the PANDABI_API_KEY environment variable. To get the key follow below steps:\n"
    "1. Go to https://www.pandabi.ai and sign up\n"
    "2. From settings go to API keys and copy\n"
    "3. Set environment variable like os.environ['PANDABI_API_KEY'] = '$2a$10$flb7....'"
)

SUPPORTED_SOURCE_CONNECTORS = {
    "mysql": "pandasai_sql",
    "postgres": "pandasai_sql",
    "cockroachdb": "pandasai_sql",
    "yahoo_finance": "pandasai_yfinance",
    "bigquery": "pandasai_bigquery",
    "snowflake": "pandasai_snowflake",
    "databricks": "pandasai_databricks",
    "oracle": "pandasai_oracle",
}

LOCAL_SOURCE_TYPES = ["csv", "parquet"]
REMOTE_SOURCE_TYPES = [
    "mysql",
    "postgres",
    "cockroachdb",
    "data",
    "yahoo_finance",
    "bigquery",
    "snowflake",
    "databricks",
    "oracle",
]
SQL_SOURCE_TYPES = ["mysql", "postgres", "cockroachdb", "oracle"]
VALID_COLUMN_TYPES = ["string", "integer", "float", "datetime", "boolean"]
VALID_TRANSFORMATION_TYPES = ["anonymize", "convert_timezone"]
