import json
import jwt
import time
import requests

from seatable_thumbnail.settings import DTABLE_PRIVATE_KEY


def get_custom_access_token(username, dtable_uuid):
    payload = {
        'exp': int(time.time()) + 60,
        'dtable_uuid': dtable_uuid,
        'username': username,
        'permission': 'rw',
    }
    access_token = jwt.encode(
        payload, DTABLE_PRIVATE_KEY, algorithm='HS256'
    )
    return access_token

def get_admin_access_token():
    access_token = jwt.encode({
        'is_db_admin': True,
        'exp': int(time.time()) + 60,
        'permission': 'rw'
    }, DTABLE_PRIVATE_KEY, 'HS256')


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


class DTableDBAPI(object):

    def __init__(self, username, dtable_uuid, dtable_db_url):
        self.username = username
        self.dtable_uuid = dtable_uuid
        self.headers = None
        self.admin_headers = None
        self.dtable_db_url = dtable_db_url.rstrip('/')
        self._init()

    def _init(self):
        db_custom_access_token = get_custom_access_token(self.username, self.dtable_uuid)
        db_admin_access_token = get_admin_access_token()
        self.headers = {'Authorization': 'Token ' + db_custom_access_token}
        self.admin_headers = {'Authorization': 'Token ' + db_admin_access_token}

    def query(self, sql, convert=False):
        url = '%s/api/v1/query/%s/?from=dtable_web' % (
            self.dtable_db_url,
            self.dtable_uuid
        )
        data = {
            'sql': sql,
            'convert_keys': convert
        }
        response = requests.post(url, json=data, headers=self.headers)
        return parse_response(response)

    def batch_update_links(self, link_info):
        '''

        :param link_info:
        including a dict such as
        {
            "link_id": "61xy",
            "table_id": "0000",
            "other_table_id": "Y2g1",
            "other_rows_ids_map": {
            "OfJdsDIaSvyqOACnm7edhA": ["OS55FMTMSZWIn3SMw7hUjw"],
            "bzPJT5Z0TL6TA-_QkzLfVw": ["I6TNJm-TTginPzASF1xv0w"]
            }
        }
        :return:
        '''
        url = '%s/api/v1/base/%s/links/?from=dtable_web' % (
            self.dtable_db_url,
            self.dtable_uuid
        )

        response = requests.post(url, json=link_info, headers=self.headers)
        return parse_response(response)

    def batch_delete_links(self, link_info):
        '''

        :param link_info: save as batch_update_links
        :return:
        '''
        url = '%s/api/v1/base/%s/links/?from=dtable_web' % (
            self.dtable_db_url,
            self.dtable_uuid
        )

        response = requests.delete(url, json=link_info, headers=self.headers)
        return parse_response(response)

    def batch_append_rows(self, table_name, rows_data):
        url = "%s/api/v1/insert-rows/%s/?from=dtable_web" % (
            self.dtable_db_url,
            self.dtable_uuid
        )

        json_data = {
            'table_name': table_name,
            'rows': rows_data,
        }
        response = requests.post(url, json=json_data, headers=self.headers)
        return parse_response(response)

    def batch_update_rows(self, table_name, updates):
        url = "%s/api/v1/update-rows/%s/?from=dtable_web" % (
            self.dtable_db_url,
            self.dtable_uuid
        )

        json_data = {
            'table_name': table_name,
            'updates': updates,
        }
        response = requests.put(url, json=json_data, headers=self.headers)
        return parse_response(response)

    def query_linked_records(self, data):
        url = '%s/api/v1/linked-records/%s/' % (self.dtable_db_url, self.dtable_uuid)
        response = requests.post(url, json=data, headers=self.headers)
        return parse_response(response)

