import json


def is_schema_source_same(schema1: dict, schema2: dict) -> bool:
    return schema1.get("source").get("type") == schema2.get("source").get(
        "type"
    ) and json.dumps(
        schema1.get("source").get("connection"), sort_keys=True
    ) == json.dumps(schema2.get("source").get("connection"), sort_keys=True)
