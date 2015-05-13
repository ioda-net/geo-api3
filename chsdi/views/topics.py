# -*- coding: utf-8 -*-

from pyramid.view import view_config

from chsdi.models.bod import Topics


@view_config(route_name='topics', renderer='jsonp')
def topics(request):
    model = Topics
    showCatalog = True
    query = request.db.query(model).filter(model.showCatalog == showCatalog).order_by(model.orderKey)
    results = [{
        'id': q.id,
        'langs': q.availableLangs,
        'showCatalog': q.showCatalog,
        'backgroundLayers': q.backgroundLayers,
        'selectedLayers': q.selectedLayers
    } for q in query]
    return {'topics': results}
