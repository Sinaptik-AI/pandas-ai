import json


def extract_json_from_json_str(json_str):
    start_index = json_str.find("```json")

    end_index = json_str.find("```", start_index)

    if start_index == -1:
        return json.loads(json_str)

    json_data = json_str[(start_index + len("```json")) : end_index].strip()

    return json.loads(json_data)
