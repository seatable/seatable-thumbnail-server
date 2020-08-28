import urllib.parse

import seatable_thumbnail.settings as settings


class HTTPRequest(object):
    def __init__(self, **scope):
        self.__dict__.update(scope)
        self.parse()

    def parse(self):
        self.parse_url()
        self.parse_query_dict()

    def parse_url(self):
        self.url = self.path[len(settings.URL_PREFIX):]

    def parse_query_dict(self):
        query_string = self.query_string.decode()
        self.query_dict = urllib.parse.parse_qs(query_string)
