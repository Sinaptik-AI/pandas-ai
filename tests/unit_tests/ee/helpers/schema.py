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
