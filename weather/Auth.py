import requests
import json
from datetime import datetime, timedelta
import os
from file import read_json_file, write_json_to_file


class Auth():

    def __init__(self):
        self.app_id, self.app_key = self.get_app_credentials()
        self.auth_url = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
        self.auth_response_file = "auth_response.json"

    def get_app_credentials(self):
        app_credentials_file = "tdx_credentials.json"
        app_credentials = read_json_file(app_credentials_file)
        app_id = app_credentials["app_id"]
        app_key = app_credentials["app_key"]
        return app_id, app_key

    def get_auth_header(self):
        content_type = 'application/x-www-form-urlencoded'
        grant_type = 'client_credentials'

        return {
            'content-type': content_type,
            'grant_type': grant_type,
            'client_id': self.app_id,
            'client_secret': self.app_key
        }

    def get_auth_response(self):
        response_raw = requests.post(self.auth_url, self.get_auth_header())
        auth_response = json.loads(response_raw.text)

        # add expire datetime
        remain_seconds_for_access = auth_response["expires_in"]
        current_datetime = datetime.now()
        expire_datetime = current_datetime + \
            timedelta(seconds=remain_seconds_for_access)
        auth_response["expire_datetime"] = expire_datetime.isoformat()

        # remove unnessary attributes
        unnessary_attributes = [
            "expires_in", "refresh_expires_in", "not-before-policy", "scope"]
        for attribute in unnessary_attributes:
            auth_response.pop(attribute)

        # save to file
        write_json_to_file(self.auth_response_file, auth_response)

    def auth_response_file_exists(self) -> bool:
        if os.path.exists(self.auth_response_file):
            return True

        return False

    def access_token_invalid(self) -> bool:
        if self.auth_response_file_exists():
            auth_response = read_json_file(self.auth_response_file)
            current_datetime = datetime.now()
            expire_datetime = datetime.fromisoformat(
                auth_response["expire_datetime"])
            # expired
            if current_datetime > expire_datetime:
                return True
            else:
                return False
        else:
            # no auth response file
            return True

    def get_access_token(self):
        if self.access_token_invalid():
            self.get_auth_response()
        auth_response = read_json_file(self.auth_response_file)

        return auth_response["access_token"]

    def get_data_header(self):
        access_token = self.get_access_token()

        return {
            'authorization': 'Bearer ' + access_token,
            'Accept-Encoding': 'gzip'
        }
