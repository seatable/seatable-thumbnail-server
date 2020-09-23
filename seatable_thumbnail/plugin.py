import requests

import seatable_thumbnail.settings as settings
from seatable_thumbnail.constants import EMPTY_BYTES
from seatable_thumbnail.utils import get_inner_path


class Plugin(object):
    def __init__(self, **info):
        self.__dict__.update(info)
        self.body = EMPTY_BYTES
        self.get()

    def get(self):
        inner_path = get_inner_path(
            settings.PLUGINS_REPO_ID, self.file_id, self.file_name)
        response = requests.get(inner_path)
        self.body = response.content
