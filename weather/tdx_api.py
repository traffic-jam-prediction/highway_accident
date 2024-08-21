import requests
from Auth import Auth
import json
from file import write_json_to_file

def get_data(api_url: str):
    auth = Auth()
    response = requests.get(api_url, headers=auth.get_data_header())
    try:
        data_response = json.loads(response.text)
    except json.decoder.JSONDecodeError:
        for attr, value in response.__dict__.items():
            print(f"{attr}: {value}")
    return data_response

def get_data_and_save_to_json(api_url: str, data_file_name: str):
    data_response = get_data(api_url)
    write_json_to_file(data_file_name, data_response)