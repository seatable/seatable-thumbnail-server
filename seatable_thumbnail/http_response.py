from seatable_thumbnail.constants import TEXT_CONTENT_TYPE, THUMBNAIL_CONTENT_TYPE


def gen_response_start(status, content_type):
    return {
        'type': 'http.response.start',
        'status': status,
        'headers': [
            [b'content-type', content_type],
        ]
    }


def gen_response_body(body):
    return {
        'type': 'http.response.body',
        'body': body,
    }


def gen_error_response(status, error_msg):
    error_start = gen_response_start(status, TEXT_CONTENT_TYPE)
    error_body = gen_response_body(error_msg.encode('utf-8'))

    return error_start, error_body


def gen_text_response(text):
    text_start = gen_response_start(200, TEXT_CONTENT_TYPE)
    text_body = gen_response_body(text.encode('utf-8'))

    return text_start, text_body


def gen_thumbnail_response(thumbnail):
    thumbnail_start = gen_response_start(200, THUMBNAIL_CONTENT_TYPE)
    thumbnail_body = gen_response_body(thumbnail)

    return thumbnail_start, thumbnail_body
