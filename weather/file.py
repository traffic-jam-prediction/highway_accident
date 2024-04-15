import json


def read_json_file(file_name: str):
    file_content = None
    with open(file=file_name, mode="r", encoding="utf-8") as file:
        file_content = json.load(file)
    return file_content

def write_json_to_file(file_name: str, json_content: dict):
    with open(file=file_name, mode='w', encoding="utf-8") as file:
        json.dump(json_content, file, indent=2, ensure_ascii=False)