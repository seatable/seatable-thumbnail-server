import os
import uuid
import json
import base64
import mimetypes
from datetime import datetime
from email.utils import formatdate

import seatable_thumbnail.settings as settings
from seatable_thumbnail.constants import TEXT_CONTENT_TYPE, FILE_EXT_TYPE_MAP, \
    IMAGE, PSD, VIDEO, XMIND
from seatable_thumbnail.models import Workspaces, DjangoSession, DTableSystemPlugins
from seatable_thumbnail.utils import get_file_id, get_file_obj


class ThumbnailSerializer(object):
    def __init__(self, db_session, request):
        self.db_session = db_session
        self.request = request
        self.check()
        self.gen_thumbnail_info()

    def check(self):
        self.params_check()
        self.session_check()
        self.resource_check()

    def gen_thumbnail_info(self):
        thumbnail_info = {}
        thumbnail_info.update(self.params)
        thumbnail_info.update(self.session_data)
        thumbnail_info.update(self.resource)
        self.thumbnail_info = thumbnail_info

    def parse_django_session(self, session_data):
        # django/contrib/sessions/backends/base.py
        encoded_data = base64.b64decode(session_data.encode('ascii'))
        hash_key, serialized = encoded_data.split(b':', 1)
        return json.loads(serialized.decode('latin-1'))

    def session_check(self):
        session_key = self.request.cookies[settings.SESSION_KEY]
        django_session = self.db_session.query(
            DjangoSession).filter_by(session_key=session_key).first()
        self.session_data = self.parse_django_session(django_session.session_data)

        username = self.session_data.get('_auth_user_name')
        external_link = self.session_data.get('external_link')
        collection_table = self.session_data.get('collection_table')
        if username:
            self.session_data['username'] = username

        if not username and not external_link and not collection_table:
            raise AssertionError(400, 'django session invalid.')

    def get_enable_file_type(self):
        enable_file_type = [IMAGE]
        if settings.ENABLE_PSD_THUMBNAIL:
            enable_file_type.append(PSD)
        if settings.ENABLE_VIDEO_THUMBNAIL:
            enable_file_type.append(VIDEO)
        if settings.ENABLE_XMIND_THUMBNAIL:
            enable_file_type.append(XMIND)
        self.enable_file_type = enable_file_type

    def params_check(self):
        size_str = self.request.query_dict.get('size', ['256'])[0]
        size = int(size_str)

        file_path = '/' + self.request.url.split('/', 3)[-1]
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1][1:].lower()
        file_type = FILE_EXT_TYPE_MAP.get(file_ext, 'Unknown')
        self.get_enable_file_type()
        if file_type not in self.enable_file_type:
            raise AssertionError(400, 'file_type invalid.')

        # url check
        url_split = self.request.url.split('/', 5)
        if not all([
            url_split[0] == 'thumbnail',
            url_split[1] == 'workspace',
            url_split[3] == 'asset',
        ]):
            raise AssertionError(400, 'url invalid.')

        #
        workspace_id = int(url_split[2])
        dtable_uuid = uuid.UUID(url_split[4]).hex

        self.params = {
            'workspace_id': workspace_id,
            'dtable_uuid': dtable_uuid,
            'size': size,
            'file_path': file_path,
            'file_name': file_name,
            'file_ext': file_ext,
            'file_type': file_type,
        }

    def resource_check(self):
        workspace_id = self.params['workspace_id']
        file_path = self.params['file_path']
        size = self.params['size']

        workspace = self.db_session.query(
            Workspaces).filter_by(id=workspace_id).first()
        repo_id = workspace.repo_id
        workspace_owner = workspace.owner
        file_obj = get_file_obj(repo_id, file_path)
        file_id = file_obj.obj_id

        thumbnail_dir = os.path.join(settings.THUMBNAIL_DIR, str(size))
        thumbnail_path = os.path.join(thumbnail_dir, file_id)
        os.makedirs(thumbnail_dir, exist_ok=True)

        last_modified_time = file_obj.mtime
        last_modified = formatdate(int(last_modified_time), usegmt=True)

        etag = '"' + file_id + '"'

        self.resource = {
            'repo_id': repo_id,
            'file_id': file_id,
            'workspace_owner': workspace_owner,
            'thumbnail_dir': thumbnail_dir,
            'thumbnail_path': thumbnail_path,
            'last_modified': last_modified,
            'etag': etag,
        }


class PluginSerializer(object):
    def __init__(self, db_session, request):
        self.db_session = db_session
        self.request = request
        self.check()
        self.gen_plugin_info()

    def check(self):
        self.params_check()
        self.resource_check()

    def gen_plugin_info(self):
        plugin_info = {}
        plugin_info.update(self.params)
        plugin_info.update(self.resource)
        self.plugin_info = plugin_info

    def params_check(self):
        plugin_name = self.request.url.split('/')[1]
        path = self.request.query_dict['path'][0]
        timestamp = self.request.query_dict['t'][0] if self.request.query_dict.get('t') else ''
        version = self.request.query_dict['version'][0] if self.request.query_dict.get('version') else ''
        content_type = mimetypes.guess_type(path)[0] if mimetypes.guess_type(path) else TEXT_CONTENT_TYPE.decode('utf-8')

        self.params = {
            'path': path,
            'plugin_name': plugin_name,
            'timestamp': timestamp,
            'version': version,
            'content_type': content_type,
        }

    def resource_check(self):
        path = self.params['path']
        plugin_name = self.params['plugin_name']

        plugin = self.db_session.query(
            DTableSystemPlugins).filter_by(name=plugin_name).first()

        file_path ='/' + plugin.name + path
        file_name = os.path.basename(file_path)
        file_id = get_file_id(settings.PLUGINS_REPO_ID, file_path)

        file_info = json.loads(plugin.info)
        last_modified_time = datetime.strptime(file_info['last_modified'][:-6], '%Y-%m-%dT%H:%M:%S')
        last_modified = formatdate(int(last_modified_time.timestamp()), usegmt=True)
        etag = '"' + file_id + '"'

        self.resource = {
            'file_path': file_path,
            'file_name': file_name,
            'file_id': file_id,
            'file_info': file_info,
            'last_modified': last_modified,
            'etag': etag,
        }
