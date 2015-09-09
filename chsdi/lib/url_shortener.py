import time

from datetime import datetime
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound
from urllib.parse import urlparse

from chsdi.models.utilities import UrlShortener


def create_short_url(request):
    url = check_url(
        request.params.get('url'), request.registry.settings
    )
    if len(url) >= UrlShortener.URL_MAX_LENGTH:
        url = request.headers['origin']

    return _add_item(request, url)


def check_url(url, config):
    if url is None:
        raise HTTPBadRequest('The parameter url is missing from the request')
    parsedUrl = urlparse(url)
    hostname = parsedUrl.hostname
    if hostname is None:
        raise HTTPBadRequest('Could not determine the hostname')
    domain = ".".join(hostname.split(".")[-2:])
    allowed_hosts = config['shortener.allowed_hosts'] if 'shortener.allowed_hosts' in config else ''
    allowed_domains = config['shortener.allowed_domains'] if 'shortener.allowed_domains' in config else ''
    if domain not in allowed_domains and hostname not in allowed_hosts:
        raise HTTPBadRequest('Shortener can only be used for %s domains or %s hosts.' % (allowed_domains, allowed_hosts))
    return url


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
        except Exception as e:  # pragma: no cover
            raise HTTPBadRequest('Error during put item %s' % e)

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


def expand_short_url(request, short_url):
    try:
        url = request.db.query(UrlShortener)\
            .filter(UrlShortener.short_url == short_url)\
            .one()
    except NoResultFound:
        return None
    else:
        return url.url
