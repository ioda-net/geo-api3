#-*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest

from chsdi.models.utilities import Communes


@view_config(route_name="communes", renderer="jsonp")
def communes(request):
    x = request.params.get('x')
    y = request.params.get('y')
    srid = request.params.get('srid')
    if x is None or y is None or srid is None:
        raise HTTPBadRequest('You must provide the coordonates and their projection')
    point = 'SRID={};POINT({} {})'.format(srid, x, y)
    commune = request.db.query(Communes)\
        .filter(Communes.the_geom.ST_Contains(point))\
        .one()
    return {'commune': commune.nom}
