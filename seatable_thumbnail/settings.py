import os
import sys


# environment
# sys.path.append('/opt/seafile/lib/python3.6/site-packages')
# os.environ['CCNET_CONF_DIR'] = '/opt/seafile/conf'
# os.environ['SEAFILE_CONF_DIR'] = '/opt/seafile/conf/seafile'
# os.environ['SEAFILE_CENTRAL_CONF_DIR'] = '/opt/seafile/conf'

#
ENABLE_VIDEO_THUMBNAIL = False
ENABLE_XMIND_THUMBNAIL = False
ENABLE_PSD_THUMBNAIL = False


# jwt
JWT_SECRET_KEY = '__Same as SeaTable JWT config __'


# url
URL_PREFIX = '/'
INNER_FILE_SERVER_ROOT = 'http://127.0.0.1:8082'


# mysql
MYSQL_USER = ''
MYSQL_PASSWORD = ''
MYSQL_HOST = ''
MYSQL_PORT = '3306'
DATABASE_NAME = ''


# dir
CONF_DIR = 'conf/'
LOG_DIR = 'logs/'
THUMBNAIL_DIR = 'thumbnail/'

# CONF_DIR = '/opt/seatable/conf/'
# LOG_DIR = '/opt/seatable/logs/'
# THUMBNAIL_DIR = '/opt/seatable/seahub-data/thumbnail/'


# size(MB) limit for generate thumbnail
THUMBNAIL_IMAGE_SIZE_LIMIT = 30
THUMBNAIL_IMAGE_ORIGINAL_SIZE_LIMIT = 256


# video use the frame at 5 second as thumbnail
THUMBNAIL_VIDEO_FRAME_TIME = 5


# ======================== local settings ======================== #
try:
    from local_settings import *
except ImportError as e:
    pass

try:
    if os.path.exists(CONF_DIR):
        sys.path.append(CONF_DIR)
    from seatable_thumbnail_settings import *
except ImportError as e:
    pass
