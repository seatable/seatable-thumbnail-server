import requests
import urllib.request
import urllib.parse

from seaserv import seafile_api
import seatable_thumbnail.settings as settings
from seatable_thumbnail.constants import EMPTY_BYTES


class Plugin(object):
    def __init__(self, **info):
        self.__dict__.update(info)
        self.body = EMPTY_BYTES
        self.get()

    def get(self):
        inner_path = self.get_inner_path()
        response = requests.get(inner_path)
        self.body = response.content

    def get_inner_path(self):
        token = seafile_api.get_fileserver_access_token(
            settings.PLUGINS_REPO_ID, self.file_id, 'view', '', use_onetime=True)
        if not token:
            raise ValueError(404, 'token not found.')
        self.inner_path = '%s/files/%s/%s' % (
            settings.INNER_FILE_SERVER_ROOT.rstrip('/'), token, urllib.parse.quote(self.file_name))

        return self.inner_path
