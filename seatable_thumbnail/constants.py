# content type
TEXT_CONTENT_TYPE = b'text/plain'
THUMBNAIL_CONTENT_TYPE = b'image/png'


# permission
PERMISSION_READ = 'r'
PERMISSION_READ_WRITE = 'rw'


# file type
EMPTY_BYTES = b''
THUMBNAIL_EXTENSION = 'png'
IMAGE_MODES = ('1', 'L', 'P', 'RGB', 'RGBA',)

TEXT = 'Text'
IMAGE = 'Image'
DOCUMENT = 'Document'
SVG = 'SVG'
PSD = 'PSD'
DRAW = 'Draw'
PDF = 'PDF'
MARKDOWN = 'Markdown'
VIDEO = 'Video'
AUDIO = 'Audio'
SPREADSHEET = 'SpreadSheet'
XMIND = 'XMind'
CDOC = 'cdoc'

PREVIEW_file_ext = {
    IMAGE: ('gif', 'jpeg', 'jpg', 'png', 'ico', 'bmp', 'tif', 'tiff',),
    DOCUMENT: ('doc', 'docx', 'ppt', 'pptx', 'odt', 'fodt', 'odp', 'fodp',),
    SPREADSHEET: ('xls', 'xlsx', 'ods', 'fods',),
    SVG: ('svg',),
    PSD: ('psd',),
    DRAW: ('draw',),
    PDF: ('pdf', 'ai',),
    MARKDOWN: ('markdown', 'md',),
    VIDEO: ('mp4', 'ogv', 'webm', 'mov',),
    AUDIO: ('mp3', 'oga', 'ogg',),
    '3D': ('stl', 'obj',),
    XMIND: ('xmind',),
    CDOC: ('cdoc',),
    TEXT: ('ac', 'am', 'bat', 'c', 'cc', 'cmake', 'cpp', 'cs', 'css', 'diff',
           'el', 'h', 'html', 'htm', 'java', 'js', 'json', 'less', 'make',
           'org', 'php', 'pl', 'properties', 'py', 'rb', 'scala', 'script',
           'sh', 'sql', 'txt', 'text', 'tex', 'vi', 'vim', 'xhtml', 'xml',
           'log', 'csv', 'groovy', 'rst', 'patch', 'go', 'yml',),
}


def gen_file_ext_type_map():
    file_ext_type_map = {}

    for file_type in list(PREVIEW_file_ext.keys()):
        for file_ext in PREVIEW_file_ext.get(file_type):
            file_ext_type_map[file_ext] = file_type

    return file_ext_type_map


FILE_EXT_TYPE_MAP = gen_file_ext_type_map()
