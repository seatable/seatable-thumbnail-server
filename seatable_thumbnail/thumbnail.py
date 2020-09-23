import os
import time
import urllib.request
import urllib.parse
import zipfile
import tempfile
from io import BytesIO
from PIL import Image
from email.utils import formatdate

from seaserv import get_repo, get_file_size
import seatable_thumbnail.settings as settings
from seatable_thumbnail.constants import IMAGE_MODES, EMPTY_BYTES,\
    THUMBNAIL_EXTENSION, IMAGE, PSD, VIDEO, XMIND
from seatable_thumbnail.utils import get_inner_path


class Thumbnail(object):
    def __init__(self, **info):
        self.__dict__.update(info)
        self.body = EMPTY_BYTES
        self.get()

    def get(self):
        if self.exist:
            with open(self.thumbnail_path, 'rb') as f:
                self.body = f.read()
        else:
            self.generate()

    def generate(self):
# ===== image =====
        if self.file_type == IMAGE:
            repo = get_repo(self.repo_id)
            file_size = get_file_size(
                repo.store_id, repo.version, self.file_id)
            if file_size > settings.THUMBNAIL_IMAGE_SIZE_LIMIT * 1024 * 1024:
                raise AssertionError(400, 'file_size invalid.')

            inner_path = get_inner_path(self.repo_id, self.file_id, self.file_name)
            image_file = urllib.request.urlopen(inner_path)
            f = BytesIO(image_file.read())

            image = Image.open(f)
            self.create_image_thumbnail(image)

# ===== psd =====
        elif self.file_type == PSD:
            from psd_tools import PSDImage

            tmp_psd = os.path.join(tempfile.gettempdir(), self.file_id)
            inner_path = get_inner_path(self.repo_id, self.file_id, self.file_name)
            urllib.request.urlretrieve(inner_path, tmp_psd)

            psd = PSDImage.open(tmp_psd)
            image = psd.topil()
            os.unlink(tmp_psd)
            self.create_image_thumbnail(image)

# ===== video =====
        elif self.file_type == VIDEO:
            from moviepy.editor import VideoFileClip

            tmp_image_path = os.path.join(
                tempfile.gettempdir(), self.file_id + '.png')
            tmp_video = os.path.join(tempfile.gettempdir(), self.file_id)
            inner_path = get_inner_path(self.repo_id, self.file_id, self.file_name)
            urllib.request.urlretrieve(inner_path, tmp_video)

            clip = VideoFileClip(tmp_video)
            clip.save_frame(
                tmp_image_path, t=settings.THUMBNAIL_VIDEO_FRAME_TIME)
            os.unlink(tmp_video)

            image = Image.open(tmp_image_path)
            os.unlink(tmp_image_path)
            self.create_image_thumbnail(image)

# ===== xmind =====
        elif self.file_type == XMIND:
            inner_path = get_inner_path(self.repo_id, self.file_id, self.file_name)
            xmind_file = urllib.request.urlopen(inner_path)
            f = BytesIO(xmind_file.read())
            xmind_zip_file = zipfile.ZipFile(f, 'r')
            xmind_thumbnail = xmind_zip_file.read('Thumbnails/thumbnail.png')
            f = BytesIO(xmind_thumbnail)

            image = Image.open(f)
            self.create_image_thumbnail(image)

    def create_image_thumbnail(self, image):
        width, height = image.size
        image_memory_cost = width * height * 4 / 1024 / 1024
        if image_memory_cost > settings.THUMBNAIL_IMAGE_ORIGINAL_SIZE_LIMIT:
            raise AssertionError('image_memory_cost invalid.')

        if image.mode not in IMAGE_MODES:
            image = image.convert('RGB')

        # save file
        image = self.get_rotated_image(image)
        image.thumbnail((self.size, self.size), Image.ANTIALIAS)
        image.save(self.thumbnail_path, THUMBNAIL_EXTENSION)
        last_modified_time = time.time()
        self.last_modified = formatdate(int(last_modified_time), usegmt=True)

        # PIL to bytes
        image_bytes = BytesIO()
        image.save(image_bytes, THUMBNAIL_EXTENSION)
        self.body = image_bytes.getvalue()

    def get_rotated_image(self, image):
        try:
            exif = image._getexif() if image._getexif() else {}
        except Exception:
            return image

        orientation = exif.get(0x0112) if isinstance(exif, dict) else 1

        if orientation == 2:
            # Vertical image
            image = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            # Rotation 180
            image = image.rotate(180)
        elif orientation == 4:
            image = image.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
            # Horizontal image
        elif orientation == 5:
            # Horizontal image + Rotation 90 CCW
            image = image.rotate(-90,
                                 expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            # Rotation 270
            image = image.rotate(-90, expand=True)
        elif orientation == 7:
            # Horizontal image + Rotation 270
            image = image.rotate(90, expand=True).transpose(
                Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            # Rotation 90
            image = image.rotate(90, expand=True)

        return image
