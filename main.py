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
                    400, 'Bad request.')
                await send(response_start)
                await send(response_body)
                return

            # permission
            try:
                permission = ThumbnailPermission(**thumbnail_info)
                if not permission.check():
                    response_start, response_body = gen_error_response(
                        403, 'Forbidden.')
                    await send(response_start)
                    await send(response_body)
                    return
            except Exception as e:
                logger.exception(e)
                response_start, response_body = gen_error_response(
                    500, 'Internal server error.')
                await send(response_start)
                await send(response_body)
                return

            # cache
            try:
                etag = thumbnail_info.get('etag')
                if_none_match_headers = request.headers.get('if-none-match')
                if_none_match = if_none_match_headers[0] if if_none_match_headers else ''

                last_modified = thumbnail_info.get('last_modified')
                if_modified_since_headers = request.headers.get('if-modified-since')
                if_modified_since = if_modified_since_headers[0] if if_modified_since_headers else ''

                if (if_none_match and if_none_match == etag) \
                        or (if_modified_since and if_modified_since == last_modified):
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
                etag = thumbnail.etag

                response_start, response_body = gen_thumbnail_response(
                    body, etag, last_modified)
                await send(response_start)
                await send(response_body)
                return
            except Exception as e:
                logger.exception(e)
                response_start, response_body = gen_error_response(
                    500, 'Internal server error.')
                await send(response_start)
                await send(response_body)
                return

# ===== Not found =====
        else:
            response_start, response_body = gen_error_response(
                404, 'Not found.')
            await send(response_start)
            await send(response_body)
            return


app = App()
