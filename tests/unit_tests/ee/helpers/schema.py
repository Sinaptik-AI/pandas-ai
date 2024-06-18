VIZ_QUERY_SCHEMA = [
    {
        "name": "Orders",
        "table": "orders",
        "measures": [
            {"name": "order_count", "type": "count"},
            {"name": "total_freight", "type": "sum", "sql": "freight"},
        ],
        "dimensions": [
            {"name": "order_id", "type": "int", "sql": "order_id"},
            {"name": "customer_id", "type": "string", "sql": "customer_id"},
            {"name": "employee_id", "type": "int", "sql": "employee_id"},
            {"name": "order_date", "type": "date", "sql": "order_date"},
            {"name": "required_date", "type": "date", "sql": "required_date"},
            {"name": "shipped_date", "type": "date", "sql": "shipped_date"},
            {"name": "ship_via", "type": "int", "sql": "ship_via"},
            {"name": "ship_name", "type": "string", "sql": "ship_name"},
            {"name": "ship_address", "type": "string", "sql": "ship_address"},
            {"name": "ship_city", "type": "string", "sql": "ship_city"},
            {"name": "ship_region", "type": "string", "sql": "ship_region"},
            {"name": "ship_postal_code", "type": "string", "sql": "ship_postal_code"},
            {"name": "ship_country", "type": "string", "sql": "ship_country"},
        ],
        "joins": [],
    }
]

VIZ_QUERY_SCHEMA_STR = '[{"name":"Orders","table":"orders","measures":[{"name":"order_count","type":"count"},{"name":"total_freight","type":"sum","sql":"freight"}],"dimensions":[{"name":"order_id","type":"int","sql":"order_id"},{"name":"customer_id","type":"string","sql":"customer_id"},{"name":"employee_id","type":"int","sql":"employee_id"},{"name":"order_date","type":"date","sql":"order_date"},{"name":"required_date","type":"date","sql":"required_date"},{"name":"shipped_date","type":"date","sql":"shipped_date"},{"name":"ship_via","type":"int","sql":"ship_via"},{"name":"ship_name","type":"string","sql":"ship_name"},{"name":"ship_address","type":"string","sql":"ship_address"},{"name":"ship_city","type":"string","sql":"ship_city"},{"name":"ship_region","type":"string","sql":"ship_region"},{"name":"ship_postal_code","type":"string","sql":"ship_postal_code"},{"name":"ship_country","type":"string","sql":"ship_country"}],"joins":[]}]'
VIZ_QUERY_SCHEMA_OBJ = '{"name":"Orders","table":"orders","measures":[{"name":"order_count","type":"count"},{"name":"total_freight","type":"sum","sql":"freight"}],"dimensions":[{"name":"order_id","type":"int","sql":"order_id"},{"name":"customer_id","type":"string","sql":"customer_id"},{"name":"employee_id","type":"int","sql":"employee_id"},{"name":"order_date","type":"date","sql":"order_date"},{"name":"required_date","type":"date","sql":"required_date"},{"name":"shipped_date","type":"date","sql":"shipped_date"},{"name":"ship_via","type":"int","sql":"ship_via"},{"name":"ship_name","type":"string","sql":"ship_name"},{"name":"ship_address","type":"string","sql":"ship_address"},{"name":"ship_city","type":"string","sql":"ship_city"},{"name":"ship_region","type":"string","sql":"ship_region"},{"name":"ship_postal_code","type":"string","sql":"ship_postal_code"},{"name":"ship_country","type":"string","sql":"ship_country"}],"joins":[]}'


STARS_SCHEMA = [
    {
        "name": "Users",
        "table": "users",
        "measures": [{"name": "user_count", "type": "count", "sql": "login"}],
        "dimensions": [
            {"name": "login", "type": "string", "sql": "login"},
            {"name": "starred_at", "type": "datetime", "sql": "starredAt"},
            {"name": "profile_url", "type": "string", "sql": "profileUrl"},
            {"name": "location", "type": "string", "sql": "location"},
            {"name": "company", "type": "string", "sql": "company"},
        ],
    }
]


MULTI_JOIN_SCHEMA = [
    {
        "name": "Sales",
        "table": "sales",
        "measures": [
            {"name": "total_revenue", "type": "sum", "sql": "revenue"},
            {"name": "total_sales", "type": "count", "sql": "id"},
        ],
        "dimensions": [
            {"name": "product", "type": "string", "sql": "product"},
            {"name": "region", "type": "string", "sql": "region"},
            {"name": "sales_date", "type": "date", "sql": "sales_date"},
            {"name": "id", "type": "string", "sql": "id"},
        ],
        "joins": [
            {
                "name": "Engagement",
                "join_type": "left",
                "sql": "${Sales.id} = ${Engagement.id}",
            }
        ],
    },
    {
        "name": "Engagement",
        "table": "engagement",
        "measures": [{"name": "total_duration", "type": "sum", "sql": "duration"}],
        "dimensions": [
            {"name": "id", "type": "string", "sql": "id"},
            {"name": "user_id", "type": "string", "sql": "user_id"},
            {"name": "activity_type", "type": "string", "sql": "activity_type"},
            {"name": "engagement_date", "type": "date", "sql": "engagement_date"},
        ],
        "joins": [
            {
                "name": "Sales",
                "join_type": "right",
                "sql": "${Engagement.id} = ${Sales.id}",
            }
        ],
    },
]
