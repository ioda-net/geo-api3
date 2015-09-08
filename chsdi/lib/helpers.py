import re
from osgeo import osr, ogr
from pyramid.httpexceptions import HTTPBadRequest
import unicodedata
from urllib.parse import quote
from urllib.parse import urlparse

import pyramid


def make_agnostic(path):
    handle_path = lambda x: x.split('://')[1] if len(x.split('://')) == 2 else path
    if path.startswith('http'):
        path = handle_path(path)
        return '//' + path
    else:
        return path


def make_api_url(request, agnostic=False):
    base_path = request.registry.settings['apache_base_path']
    base_path = '' if base_path == 'main' else '/' + base_path
    host = request.host + base_path if 'localhost' not in request.host else request.host
    if agnostic:
        return ''.join(('//', host))
    else:
        return ''.join((request.scheme, '://', host))


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


def round(val):
    import math
    return math.floor(val + 0.5)


def format_search_text(input_str):
    return remove_accents(
        escape_sphinx_syntax(input_str)
    )


def remove_accents(input_str):
    if input_str is None:  # pragma: no cover
        return input_str
    input_str = input_str.translate(str.maketrans({
        'Ü': 'ue',
        'ä': 'ae',
        'Ä': 'ae',
        'ö': 'oe',
        'Ö': 'oe',
        'ü': 'ue',
    }))
    return ''.join(c for c in unicodedata.normalize('NFD', input_str) if unicodedata.category(c) != 'Mn')


def escape_sphinx_syntax(input_str):
    if input_str is None:  # pragma: no cover
        return input_str
    return input_str.translate(str.maketrans({
        '|': r'\|',
        '!': r'\!',
        '@': r'\@',
        '&': r'\&',
        '~': r'\~',
        '^': r'\^',
        '=': r'\=',
        '/': r'\/',
        '(': r'\(',
        ')': r'\)',
        ']': r'\]',
        '[': r'\[',
        '*': r'\*',
        '<': r'\<',
        '$': r'\$',
        '"': r'\"',
    }))


def quoting(text):
    return quote(text.encode('utf-8'))


def transformCoordinate(wkt, srid_from, srid_to):
    srid_in = osr.SpatialReference()
    srid_in.ImportFromEPSG(srid_from)
    srid_out = osr.SpatialReference()
    srid_out.ImportFromEPSG(srid_to)
    geom = ogr.CreateGeometryFromWkt(wkt)
    geom.AssignSpatialReference(srid_in)
    geom.TransformTo(srid_out)
    return geom


def get_configuration():
    registry = pyramid.threadlocal.get_current_registry()
    return registry.settings


def get_from_configuration(key):
    return get_configuration().get(key, None)
