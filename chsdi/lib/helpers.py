import pyramid
import unicodedata

import math
from osgeo import osr, ogr


def round(val):
    '''The builtin round function rounds even numbers down and odd numbers up. This avoids a round
    up bias and is conform to floating point manipulation defined by the IEEE. Since we want to
    round number in .5 up and the others down, we add 0.5 to the value and take the floor.
    '''
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
    return ''.join(c for c in unicodedata.normalize('NFD', input_str)
                   if unicodedata.category(c) != 'Mn')


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


def float_raise_nan(val):
    """float('NaN') does not raise an Exception. This function does."""
    ret = float(val)
    if math.isnan(ret):
        raise ValueError('nan is not considered valid float')
    return ret
