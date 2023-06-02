import logging

from seatable_thumbnail import DBSession
from seatable_thumbnail.serializers import ThumbnailSerializer, PluginSerializer
from seatable_thumbnail.permissions import ThumbnailPermission
from seatable_thumbnail.thumbnail import Thumbnail
from seatable_thumbnail.plugin import Plugin
from seatable_thumbnail.http_request import HTTPRequest
from seatable_thumbnail.http_response import gen_error_response, gen_plugin_response, \
    gen_text_response, gen_thumbnail_response, gen_cache_response
from seatable_thumbnail.utils import cache_check

logger = logging.getLogger(__name__)


class App:
    async def __call__(self, scope, receive, send):
        """
        Docs: https://www.uvicorn.org/
        """
        # request
        request = HTTPRequest(**scope)
        print('request.url: ', request.url)
        print('request.url[:10]: ', request.url[:10])
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
            print('into thumbnail...')
            db_session = DBSession()

            # serializer
            try:
                serializer = ThumbnailSerializer(db_session, request)
                thumbnail_info = serializer.thumbnail_info
            except Exception as e:
                logger.exception(e)
                db_session.close()
                response_start, response_body = gen_error_response(
                    400, 'Bad request.')
                await send(response_start)
                await send(response_body)
                return

            # permission
            try:
                permission = ThumbnailPermission(db_session, **thumbnail_info)
                if not permission.check():
                    db_session.close()
                    response_start, response_body = gen_error_response(
                        403, 'Forbidden.')
                    await send(response_start)
                    await send(response_body)
                    return
            except Exception as e:
                logger.exception(e)
                db_session.close()
                response_start, response_body = gen_error_response(
                    500, 'Internal server error.')
                await send(response_start)
                await send(response_body)
                return

            db_session.close()

            # cache
            try:
                if cache_check(request, thumbnail_info):
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

# ===== plugin =====
        elif 'dtable-plugins/' == request.url[:15]:
            db_session = DBSession()

            # serializer
            try:
                serializer = PluginSerializer(db_session, request)
                plugin_info = serializer.plugin_info
            except Exception as e:
                logger.exception(e)
                db_session.close()
                response_start, response_body = gen_error_response(
                    400, 'Bad request.')
                await send(response_start)
                await send(response_body)
                return

            db_session.close()

            # cache
            try:
                if cache_check(request, plugin_info):
                    response_start, response_body = gen_cache_response()
                    await send(response_start)
                    await send(response_body)
                    return
            except Exception as e:
                logger.exception(e)

            # get
            try:
                plugin = Plugin(**plugin_info)
                body = plugin.body
                content_type = plugin.content_type
                last_modified = plugin.last_modified
                etag = plugin.etag

                response_start, response_body = gen_plugin_response(
                    body, content_type, etag, last_modified)
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
