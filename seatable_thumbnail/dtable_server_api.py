import json
import time

import jwt
import requests

from seatable_thumbnail import settings


def get_dtable_server_token(username, dtable_uuid):

    payload = {
        'exp': int(time.time()) + 60,
        'dtable_uuid': dtable_uuid,
        'username': username,
        'permission': 'rw',
    }
    access_token = jwt.encode(
        payload, settings.DTABLE_PRIVATE_KEY, algorithm='HS256'
    )

    return access_token

def parse_response(response):
    if response.status_code >= 400:
        raise ConnectionError(response.status_code, response.text)
    else:
        try:
            data = json.loads(response.text)
            return data
        except:
            pass


class DTableServerAPI(object):
    # simple version of python sdk without authorization for base or table manipulation

    def __init__(self, username, dtable_uuid, dtable_server_url, server_url=None, workspace_id=None, repo_id=None):
        self.username = username
        self.dtable_uuid = dtable_uuid
        self.headers = None
        self.dtable_server_url = dtable_server_url.rstrip('/')
        self.workspace_id = workspace_id
        self.timeout = 30
        self.server_url = server_url.strip('/') if server_url else None
        self.repo_id = repo_id
        self._init()

    def _init(self):
        dtable_server_access_token = get_dtable_server_token(self.username, self.dtable_uuid)
        self.headers = {'Authorization': 'Token ' + dtable_server_access_token}

    def get_metadata(self):
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/metadata/?from=dtable_web'
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        data = parse_response(response)
        return data.get('metadata')

    def get_row(self, table_name, row_id, timeout=None):
        """
        :param table_name: str
        :param row_id: str
        :return: dict
        """
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/rows/' + row_id + '/?from=dtable_web'
        params = {
            'table_name': table_name,
        }
        response = requests.get(url, params=params, headers=self.headers, timeout=timeout)
        data = parse_response(response)
        return data

    def get_row_by_table_id(self, table_id, row_id, convert=None, timeout=None):
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/rows/' + row_id + '/?from=dtable_web'
        params = {
            'table_id': table_id,
        }
        if convert is not None:
            params['convert'] = convert
        response = requests.get(url, params=params, headers=self.headers, timeout=timeout)
        data = parse_response(response)
        return data

    def list_rows(self, table_name):
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/rows/?from=dtable_web'
        params = {
            'table_name': table_name,
        }
        response = requests.get(url, params=params, headers=self.headers)
        data = parse_response(response)
        return data.get('rows')

    def append_row(self, table_name, row_data):
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/rows/?from=dtable_web'
        json_data = {
            'table_name': table_name,
            'row': row_data,
        }
        response = requests.post(url, json=json_data, headers=self.headers)
        return parse_response(response)

    def batch_append_rows(self, table_name, rows_data, return_rows=False):
        """
        :param table_name: str
        :param rows_data: dict
        """
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/batch-append-rows/?from=dtable_web'
        json_data = {
            'table_name': table_name,
            'rows': rows_data,
            'return_rows': return_rows
        }
        response = requests.post(url, json=json_data, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def update_row(self, table_name, row_id, row_data):
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/rows/?from=dtable_web'
        json_data = {
            'table_name': table_name,
            'row_id': row_id,
            'row': row_data,
        }
        response = requests.put(url, json=json_data, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def list_columns(self, table_name, view_name=None):
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/columns/?from=dtable_web'
        params = {
            'table_name': table_name,
        }
        if view_name:
            params['view_name'] = view_name
        response = requests.get(url, params=params, headers=self.headers)
        data = parse_response(response)
        return data.get('columns')

    def update_link(self, link_id, table_id, other_table_id, row_id, other_rows_ids):
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/links/?from=dtable_web'
        json_data = {
            'link_id': link_id,
            'table_id': table_id,
            'other_table_id': other_table_id,
            'row_id': row_id,
            'other_rows_ids': other_rows_ids,
        }
        response = requests.put(url, json=json_data, headers=self.headers)
        return parse_response(response)

    def add_table(self, table_name, lang='en', columns=None):
        """
        :param table_name: str
        :param lang: str, currently 'en' for English, and 'zh-cn' for Chinese
        :param columns: list
        """
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/tables/?from=dtable_web'
        json_data = {
            'table_name': table_name,
            'lang': lang,
        }
        if columns:
            json_data['columns'] = columns
        response = requests.post(url, json=json_data, headers=self.headers, timeout=self.timeout)
        return parse_response(response)

    def create_snapshot(self, dtable_name):
        url = self.dtable_server_url + '/api/v1/dtables/' + self.dtable_uuid + '/snapshot/?from=dtable_web'
        json_data = {
            'dtable_name': dtable_name,
        }
        response = requests.post(url, json=json_data, headers=self.headers, timeout=self.timeout)
        data = parse_response(response)

        return data
