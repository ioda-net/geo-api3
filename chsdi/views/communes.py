#-*- coding: utf-8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.orm.exc import NoResultFound

from chsdi.models.utilities import Communes


@view_config(route_name="communes", renderer="jsonp")
def communes(request):
    x = request.params.get('x')
    y = request.params.get('y')
    if not x or not y:
        raise HTTPBadRequest('You must provide the coordonates.')
    point = 'SRID={};POINT({} {})'.format(21781, x, y)
    try:
        commune = request.db.query(Communes)\
            .filter(Communes.the_geom.ST_Contains(point))\
            .one()
    except NoResultFound:
        return {}
    else:
        return {'commune': commune.nom}
