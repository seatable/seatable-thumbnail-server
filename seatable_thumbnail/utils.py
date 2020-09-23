import urllib.request
import urllib.parse

from seaserv import seafile_api
import seatable_thumbnail.settings as settings


def get_file_id(repo_id, file_path):
    file_id = seafile_api.get_file_id_by_path(repo_id, file_path)
    if not file_id:
        raise ValueError(404, 'file_id not found.')

    return file_id


def get_inner_path(repo_id, file_id, file_name):
    token = seafile_api.get_fileserver_access_token(
        repo_id, file_id, 'view', '', use_onetime=True)
    if not token:
        raise ValueError(404, 'token not found.')
    inner_path = '%s/files/%s/%s' % (
        settings.INNER_FILE_SERVER_ROOT.rstrip('/'), token, urllib.parse.quote(file_name))

    return inner_path


def cache_check(request, info):
    etag = info.get('etag')
    if_none_match_headers = request.headers.get('if-none-match')
    if_none_match = if_none_match_headers[0] if if_none_match_headers else ''

    last_modified = info.get('last_modified')
    if_modified_since_headers = request.headers.get('if-modified-since')
    if_modified_since = if_modified_since_headers[0] if if_modified_since_headers else ''

    if (if_none_match and if_none_match == etag) \
            or (if_modified_since and if_modified_since == last_modified):
        return True
    else:
        return False
