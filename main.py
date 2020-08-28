import logging

from seatable_thumbnail.validators import ThumbnailValidator
from seatable_thumbnail.thumbnail import Thumbnail
from seatable_thumbnail.http_request import HTTPRequest
from seatable_thumbnail.http_response import gen_error_response, \
    gen_text_response, gen_thumbnail_response

logger = logging.getLogger(__name__)


class App:
    async def __call__(self, scope, receive, send):
        """
        Docs: https://www.uvicorn.org/
        """
        # request
        request = HTTPRequest(**scope)
        if request.method != 'GET':
            error_start, error_body = gen_error_response(
                405, 'Method %s not allowed.' % request.method)
            await send(error_start)
            await send(error_body)
            return

        # router
# ===== ping =====
        if request.url in ('ping', 'ping/'):
            text_start, text_body = gen_text_response('pong')
            await send(text_start)
            await send(text_body)
            return

# ===== thumbnail =====
        elif 'thumbnail/' in request.url:
            # check
            try:
                validator = ThumbnailValidator(request)
                thumbnail_info = validator.thumbnail_info
            except Exception as e:
                logger.error(e)
                error_start, error_body = gen_error_response(
                    400, 'Request invalid.')
                await send(error_start)
                await send(error_body)
                return

            # get or generate
            try:
                thumbnail = Thumbnail(**thumbnail_info)
                body = thumbnail.body
                thumbnail_start, thumbnail_body = gen_thumbnail_response(body)
                # send
                await send(thumbnail_start)
                await send(thumbnail_body)
                return
            except Exception as e:
                logger.error(e)
                error_start, error_body = gen_error_response(
                    500, 'Generate failed.')
                await send(error_start)
                await send(error_body)
                return

# ===== Not found =====
        else:
            error_start, error_body = gen_error_response(
                404, 'Not Found.')
            await send(error_start)
            await send(error_body)
            return


app = App()
