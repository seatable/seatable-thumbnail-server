from seatable_thumbnail.constants import TEXT_CONTENT_TYPE, THUMBNAIL_CONTENT_TYPE, \
    EMPTY_BYTES


def gen_response_start(status, content_type):
    return {
        'type': 'http.response.start',
        'status': status,
        'headers': [
            [b'Content-Type', content_type],
        ]
    }


def gen_response_body(body):
    return {
        'type': 'http.response.body',
        'body': body,
    }


def gen_error_response(status, error_msg):
    response_start = gen_response_start(status, TEXT_CONTENT_TYPE)
    response_body = gen_response_body(error_msg.encode('utf-8'))

    return response_start, response_body


def gen_text_response(text):
    response_start = gen_response_start(200, TEXT_CONTENT_TYPE)
    response_body = gen_response_body(text.encode('utf-8'))

    return response_start, response_body


def gen_cache_response():
    response_start = gen_response_start(304, THUMBNAIL_CONTENT_TYPE)
    response_body = gen_response_body(EMPTY_BYTES)

    return response_start, response_body


def gen_thumbnail_response(thumbnail, etag, last_modified):
    response_start = gen_response_start(200, THUMBNAIL_CONTENT_TYPE)
    response_body = gen_response_body(thumbnail)

    # cache
    if thumbnail:
        response_start['headers'].append([b'Cache-Control', b'max-age=86400, public'])
        response_start['headers'].append([b'ETag', etag.encode('utf-8')])
        response_start['headers'].append([b'Last-Modified', last_modified.encode('utf-8')])

    return response_start, response_body
