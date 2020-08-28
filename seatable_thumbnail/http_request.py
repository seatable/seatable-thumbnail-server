import urllib.parse

import seatable_thumbnail.settings as settings


class HTTPRequest(object):
    def __init__(self, **scope):
        self.__dict__.update(scope)
        self.parse()

    def parse(self):
        self.parse_headers()
        self.parse_url()
        self.parse_query_dict()

    def parse_headers(self):
        raw_headers = self.headers
        headers = {}
        for item in raw_headers:
            k = item[0].decode().lower()
            v = item[1].decode()
            headers[k] = v
        self.headers = headers

    def parse_url(self):
        self.url = self.path[len(settings.URL_PREFIX):]

    def parse_query_dict(self):
        query_string = self.query_string.decode()
        self.query_dict = urllib.parse.parse_qs(query_string)
