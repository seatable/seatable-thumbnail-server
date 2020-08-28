import os
import jwt
import uuid

from seaserv import seafile_api
import seatable_thumbnail.settings as settings
from seatable_thumbnail.constants import FILE_EXT_TYPE_MAP, JWT_AUTH_HEADER_PREFIX, \
    JWT_VERIFY, JWT_LEEWAY, JWT_AUDIENCE, JWT_ISSUER, JWT_ALGORITHM, \
    IMAGE, PSD, VIDEO, XMIND


class ThumbnailValidator(object):
    def __init__(self, request):
        self.request = request
        self.check()
        self.gen_thumbnail_info()

    def check(self):
        self.jwt_check()
        self.params_check()
        self.resource_check()
        self.gen_thumbnail_info()

    def gen_thumbnail_info(self):
        thumbnail_info = {}
        thumbnail_info.update(self.payload)
        thumbnail_info.update(self.params)
        thumbnail_info.update(self.resource)
        self.thumbnail_info = thumbnail_info

    def jwt_decode_handler(self, jwt_token):
        options = {
            'verify_exp': True,
        }
        return jwt.decode(
            jwt_token,
            settings.JWT_SECRET_KEY,
            JWT_VERIFY,
            options=options,
            leeway=JWT_LEEWAY,
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
            algorithms=[JWT_ALGORITHM]
        )

    def jwt_check(self):
        jwt_token = self.request.headers['authorization'][
            len(JWT_AUTH_HEADER_PREFIX):]
        self.payload = self.jwt_decode_handler(jwt_token)

        # permission check
        if 'r' not in self.payload['permission']:
            raise AssertionError(403, 'permission denied.')

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
        size_str = self.request.query_dict['size'][0]
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

        # dtable_uuid check
        workspace_id = int(url_split[2])
        dtable_uuid = url_split[4]
        dtable_uuid = uuid.UUID(dtable_uuid).hex
        if dtable_uuid != self.payload['dtable_uuid']:
            raise AssertionError(400, 'dtable_uuid invalid.')

        self.params = {
            'workspace_id': workspace_id,
            'size': size,
            'file_path': file_path,
            'file_name': file_name,
            'file_ext': file_ext,
            'file_type': file_type,
        }

    def resource_check(self):
        repo_id = self.payload['repo_id']
        file_path = self.params['file_path']
        size = self.params['size']
        file_id = seafile_api.get_file_id_by_path(repo_id, file_path)
        if not file_id:
            raise ValueError(404, 'file_id not found.')

        thumbnail_dir = os.path.join(settings.THUMBNAIL_DIR, str(size))
        thumbnail_path = os.path.join(thumbnail_dir, file_id)
        os.makedirs(thumbnail_dir, exist_ok=True)

        self.resource = {
            'file_id': file_id,
            'thumbnail_dir': thumbnail_dir,
            'thumbnail_path': thumbnail_path,
        }
