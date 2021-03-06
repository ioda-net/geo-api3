from functools import wraps
import xml.parsers.expat

import pyramid.httpexceptions as exc

import urllib


EXPECTED_CONTENT_TYPE = 'application/vnd.google-earth.kml+xml'


def validate_kml_input():
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            request = getattr(self, 'request', self)

            MAX_FILE_SIZE = 1024 * 1024 * 2

            # IE9 simply doesn't send content_type header. So we set it ourself
            if request.user_agent is not None and 'MSIE 9.0' in request.user_agent:
                request.content_type = EXPECTED_CONTENT_TYPE

            if request.content_type != EXPECTED_CONTENT_TYPE:
                raise exc.HTTPUnsupportedMediaType('Only KML file are accepted')

            # IE9 sends data urlencoded
            # body must be decoded in order for validation to work
            data = urllib.parse.unquote_plus(request.body.decode('utf-8'))
            if len(data) > MAX_FILE_SIZE:
                raise exc.HTTPRequestEntityTooLarge('File size exceed %s bytes' % MAX_FILE_SIZE)
            try:
                p = xml.parsers.expat.ParserCreate()
                p.Parse(data)
            except Exception:
                raise exc.HTTPUnsupportedMediaType('Only valid KML file are accepted')

            # request.body must be of type bytes
            request.body = data.encode('utf-8')

            return func(self, *args, **kwargs)
        return wrapper
    return decorator
