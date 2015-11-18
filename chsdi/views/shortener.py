from pyramid.view import view_config

import pyramid.httpexceptions as exc

from chsdi.lib.url_shortener import create_short_url
from chsdi.lib.url_shortener import expand_short_url


@view_config(route_name='shorten', renderer='jsonp')
def shortener(request):
    short_url = create_short_url(request)
    return {
        'shorturl': short_url
    }


@view_config(route_name='shorten_redirect')
def shorten_redirect(request):
    short_url = request.matchdict.get('id')
    if short_url is None:  # pragma: no cover
        raise exc.HTTPBadRequest('Please provide an id')

    url = expand_short_url(request, short_url)
    if url is None:
        message = 'This short url doesn\'t exist: http://{}/{}'\
            .format(request.registry.settings['shortener.host'], short_url)
        raise exc.HTTPBadRequest(message)
    raise exc.HTTPMovedPermanently(location=url)
