# -*- coding: utf-8 -*-

from pyramid.view import view_config
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

import pyramid.httpexceptions as exc
import time

from chsdi.models.utilities import UrlShortener
from chsdi.lib.helpers import check_url


def _add_item(request, url):
    short_url = _get_short_url(request, url)
    if short_url is None:
        # Create a new short url if url not in DB
        # Magic number relates to the initial epoch
        t = int(time.time() * 1000) - 1000000000000
        short_url = '{:x}'.format(t)
        try:
            shorten_url = UrlShortener(url=url, short_url=short_url, createtime=datetime.now())
            request.db.add(shorten_url)
            request.db.commit()
        except Exception as e:
            raise exc.HTTPBadRequest('Error during put item %s' % e)

    return short_url


def _get_short_url(request, url):
    try:
        shorten_url = request.db.query(UrlShortener)\
            .filter(UrlShortener.url == url)\
            .one()
    except NoResultFound:
        return None
    else:
        return shorten_url.short_url


def _get_url(request, short_url):
    try:
        url = request.db.query(UrlShortener)\
            .filter(UrlShortener.short_url == short_url)\
            .one()
    except NoResultFound:
        return None
    else:
        return url.url


@view_config(route_name='shorten', renderer='jsonp')
def shortener(request):
    url = check_url(
        request.params.get('url'), request.registry.settings
    )
    if len(url) >= UrlShortener.URL_MAX_LENGTH:
        url = request.headers['origin']

    short_url = _add_item(request, url)
    return {
        'shorturl': '{}://{}/shorten/{}'.format(
            request.scheme,
            request.registry.settings['shortener.host'],
            short_url
        )
    }


@view_config(route_name='shorten_redirect')
def shorten_redirect(request):
    short_url = request.matchdict.get('id')
    if short_url is None:
        raise exc.HTTPBadRequest('Please provide an id')

    url = _get_url(request, short_url)
    if url is None:
        raise exc.HTTPBadRequest('This short url doesn\'t exist: http://{}/{}'.format(request.registry.settings['shortener.host'], short_url))
    raise exc.HTTPMovedPermanently(location=url)
