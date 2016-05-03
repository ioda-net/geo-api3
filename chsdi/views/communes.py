import logging

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
)

from chsdi.models.utilities import Communes


@view_config(route_name="communes", renderer="jsonp")
def communes(request):
    x = request.params.get('x')
    y = request.params.get('y')
    if not x or not y:
        raise HTTPBadRequest('You must provide the coordonates.')
    geom_srid = Communes.the_geom.property.columns[0].type.srid
    point = 'SRID={};POINT({} {})'.format(geom_srid, x, y)
    try:
        commune = request.db.query(Communes)\
            .filter(Communes.the_geom.ST_Contains(point))\
            .one()
    except (NoResultFound, MultipleResultsFound) as e:
        logging.error(e)
        return {}
    else:
        return {'commune': commune.nom}
