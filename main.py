import logging

from seatable_thumbnail.serializers import ThumbnailSerializer
from seatable_thumbnail.permissions import ThumbnailPermission
from seatable_thumbnail.thumbnail import Thumbnail
from seatable_thumbnail.http_request import HTTPRequest
from seatable_thumbnail.http_response import gen_error_response, \
    gen_text_response, gen_thumbnail_response, gen_cache_response

logger = logging.getLogger(__name__)


class App:
    async def __call__(self, scope, receive, send):
        """
        Docs: https://www.uvicorn.org/
        """
        # request
        request = HTTPRequest(**scope)
        if request.method != 'GET':
            response_start, response_body = gen_error_response(
                405, 'Method %s not allowed.' % request.method)
            await send(response_start)
            await send(response_body)
            return

        # router
# ===== ping =====
        if request.url in ('ping', 'ping/'):
            response_start, response_body = gen_text_response('pong')
            await send(response_start)
            await send(response_body)
            return

# ===== thumbnail =====
        elif 'thumbnail/' == request.url[:10]:
            # serializer
            try:
                serializer = ThumbnailSerializer(request)
                thumbnail_info = serializer.thumbnail_info
            except Exception as e:
                logger.exception(e)
                response_start, response_body = gen_error_response(
                    400, 'Request invalid.')
                await send(response_start)
                await send(response_body)
                return

            # permission
            try:
                permission = ThumbnailPermission(**thumbnail_info)
            except Exception as e:
                logger.exception(e)
                response_start, response_body = gen_error_response(
                    403, 'Forbidden.')
                await send(response_start)
                await send(response_body)
                return

            # cache
            try:
                if_modified_since_list = request.headers.get('if-modified-since')
                if if_modified_since_list:
                    if_modified_since = if_modified_since_list[0].encode('utf-8')
                    last_modified = thumbnail_info.get('last_modified')
                    if if_modified_since and last_modified \
                            and if_modified_since == last_modified:
                        response_start, response_body = gen_cache_response()
                        await send(response_start)
                        await send(response_body)
                        return
            except Exception as e:
                logger.exception(e)

            # get or generate
            try:
                thumbnail = Thumbnail(**thumbnail_info)
                body = thumbnail.body
                last_modified = thumbnail.last_modified
                # send
                response_start, response_body = gen_thumbnail_response(body, last_modified)
                await send(response_start)
                await send(response_body)
                return
            except Exception as e:
                logger.exception(e)
                response_start, response_body = gen_error_response(
                    500, 'Generate failed.')
                await send(response_start)
                await send(response_body)
                return

# ===== Not found =====
        else:
            response_start, response_body = gen_error_response(
                404, 'Not Found.')
            await send(response_start)
            await send(response_body)
            return


app = App()
