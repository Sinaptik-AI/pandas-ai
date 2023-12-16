# Connectors

## Overview

PandasAI mission is to make data analysis and manipulation more efficient and accessible to everyone. This includes making it easier to connect to data sources and to use them in your data analysis and manipulation workflow.

PandasAI provides a number of connectors that allow you to connect to different data sources. These connectors are designed to be easy to use, even if you are not familiar with the data source or with PandasAI.

To use a connector, you first need to install the required dependencies. You can do this by running the following command:

```console
# Using poetry (recommended)
poetry add pandasai[connectors]
# Using pip
pip install pandasai[connectors]
```

Have a look at the video of how to use the connectors:
[![Intro to Connectors](https://cdn.loom.com/sessions/thumbnails/db24dea5a9e0428b87ad86ff596d5f7c-00001.jpg)](https://www.loom.com/embed/db24dea5a9e0428b87ad86ff596d5f7c?sid=0593ef29-9f5c-418a-a9ef-c0537c57d2ad "Intro to Connectors")

## SQL connectors

PandasAI provides connectors for the following SQL databases:

- PostgreSQL
- MySQL
- Generic SQL
- Snowflake
- DataBricks
- Yahoo Finance

Additionally, PandasAI provides a generic SQL connector that can be used to connect to any SQL database.

### PostgreSQL connector

The PostgreSQL connector allows you to connect to a PostgreSQL database. It is designed to be easy to use, even if you are not familiar with PostgreSQL or with PandasAI.

To use the PostgreSQL connector, you only need to import it into your Python code and pass it to a `SmartDataframe` or `SmartDatalake` object:

```python
from pandasai import SmartDataframe
from pandasai.connectors import PostgreSQLConnector

postgres_connector = PostgreSQLConnector(
    config={
        "host": "localhost",
        "port": 5432,
        "database": "mydb",
        "username": "root",
        "password": "root",
        "table": "payments",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["payment_status", "=", "PAIDOFF"],
        ],
    }
)

df = SmartDataframe(postgres_connector)
df.chat('What is the total amount of payments in the last year?')
```

### MySQL connector

Similarly to the PostgreSQL connector, the MySQL connector allows you to connect to a MySQL database. It is designed to be easy to use, even if you are not familiar with MySQL or with PandasAI.

To use the MySQL connector, you only need to import it into your Python code and pass it to a `SmartDataframe` or `SmartDatalake` object:

```python
from pandasai import SmartDataframe
from pandasai.connectors import MySQLConnector

mysql_connector = MySQLConnector(
    config={
        "host": "localhost",
        "port": 3306,
        "database": "mydb",
        "username": "root",
        "password": "root",
        "table": "loans",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["loan_status", "=", "PAIDOFF"],
        ],
    }
)

df = SmartDataframe(mysql_connector)
df.chat('What is the total amount of loans in the last year?')
```

### Sqlite connector

Similarly to the PostgreSQL and MySQL connectors, the Sqlite connector allows you to connect to a local Sqlite database file. It is designed to be easy to use, even if you are not familiar with Sqlite or with PandasAI.

To use the Sqlite connector, you only need to import it into your Python code and pass it to a `SmartDataframe` or `SmartDatalake` object:

```python
from pandasai import SmartDataframe
from pandasai.connectors import SqliteConnector

connector = SqliteConnector(config={
    "database" : "PATH_TO_DB",
    "table" : "actor",
    "where" :[
        ["first_name","=","PENELOPE"]
    ]
})

df = SmartDataframe(connector)
df.chat('How many records are there ?')
```


### Generic SQL connector

The generic SQL connector allows you to connect to any SQL database that is supported by SQLAlchemy.

To use the generic SQL connector, you only need to import it into your Python code and pass it to a `SmartDataframe` or `SmartDatalake` object:

```python
from pandasai.connectors import SQLConnector

sql_connector = SQLConnector(
    config={
        "dialect": "sqlite",
        "driver": "pysqlite",
        "host": "localhost",
        "port": 3306,
        "database": "mydb",
        "username": "root",
        "password": "root",
        "table": "loans",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["loan_status", "=", "PAIDOFF"],
        ],
    }
)
```

## Snowflake connector

The Snowflake connector allows you to connect to Snowflake. It is very similar to the SQL connectors, but it has some differences.

To use the Snowflake connector, you only need to import it into your Python code and pass it to a `SmartDataframe` or `SmartDatalake` object:

```python
from pandasai import SmartDataframe
from pandasai.connectors import SnowFlakeConnector

snowflake_connector = SnowFlakeConnector(
    config={
        "account": "ehxzojy-ue47135",
        "database": "SNOWFLAKE_SAMPLE_DATA",
        "username": "test",
        "password": "*****",
        "table": "lineitem",
        "warehouse": "COMPUTE_WH",
        "dbSchema": "tpch_sf1",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["l_quantity", ">", "49"]
        ],
    }
)

df = SmartDataframe(snowflake_connector)
df.chat("How many records has status 'F'?")
```

## DataBricks connector

The DataBricks connector allows you to connect to DataBricks. It is very similar to the SQL connectors, but it has some differences.

To use the DataBricks connector, you only need to import it into your Python code and pass it to a `SmartDataframe` or `SmartDatalake` object:

```python
from pandasai.connectors import DatabricksConnector

databricks_connector = DatabricksConnector(
    config={
        "host": "adb-*****.azuredatabricks.net",
        "database": "default",
        "token": "dapidfd412321",
        "port": 443,
        "table": "loan_payments_data",
        "httpPath": "/sql/1.0/warehouses/213421312",
        "where": [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["loan_status", "=", "PAIDOFF"],
        ],
    }
)
```

## Yahoo Finance connector

The Yahoo Finance connector allows you to connect to Yahoo Finance, by simply passing the ticker symbol of the stock you want to analyze.

To use the Yahoo Finance connector, you only need to import it into your Python code and pass it to a `SmartDataframe` or `SmartDatalake` object:

```python
from pandasai import SmartDataframe
from pandasai.connectors.yahoo_finance import YahooFinanceConnector

yahoo_connector = YahooFinanceConnector("MSFT")

df = SmartDataframe(yahoo_connector)
df.chat("What is the closing price for yesterday?")
```

## Airtable Connector

The Airtable connector allows you to connect to Airtable Projects Tables, by simply passing the `base_id` , `api_key` and `table_name` of the table you want to analyze.

To use the Airtable connector, you only need to import it into your Python code and pass it to a `SmartDataframe` or `SmartDatalake` object:

```python
from pandasai.connectors import AirtableConnector
from pandasai import SmartDataframe


airtable_connectors = AirtableConnector(
    config={
        "api_key": "AIRTABLE_API_TOKEN",
        "table":"AIRTABLE_TABLE_NAME",
        "base_id":"AIRTABLE_BASE_ID",
        "where" : [
            # this is optional and filters the data to
            # reduce the size of the dataframe
            ["Status" ,"=","In progress"]
        ]
    }
)

df = SmartDataframe(airtable_connectors)

df.chat("How many rows are there in data ?")
```