from pyramid.config import Configurator
from pyramid.renderers import JSONP
from sqlalchemy.orm import scoped_session, sessionmaker

from chsdi.customers.views import register_customer_view
from chsdi.renderers import EsriJSON, CSVRenderer
from chsdi.models import initialize_sql
from papyrus.renderers import GeoJSON
from chsdi.lib.raster.georaster import init_rasterfiles


def db(request):
    maker = request.registry.dbmaker
    session = maker()

    def cleanup(request):
        session.close()
    request.add_finished_callback(cleanup)

    return session


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    app_version = settings.get('app_version')
    settings['app_version'] = app_version
    config = Configurator(settings=settings)
    config.include('pyramid_mako')

    # init raster files for height/profile and preload COMB file
    init_rasterfiles(
        settings['dtm_base_path'],
        settings['raster.preloaded'].split(','))

    # renderers
    config.add_mako_renderer('.html')
    config.add_mako_renderer('.js')
    config.add_renderer('jsonp', JSONP(param_name='callback', indent=None, separators=(',', ':')))
    config.add_renderer('geojson', GeoJSON(jsonp_param_name='callback'))
    config.add_renderer('esrijson', EsriJSON(jsonp_param_name='callback'))
    config.add_renderer('csv', CSVRenderer)

    # sql section
    config.registry.dbmaker = scoped_session(sessionmaker())
    config.add_request_method(db, reify=True)
    initialize_sql(settings)

    # route definitions
    config.add_route('ogcproxy', '/{portal}/ogcproxy')
    config.add_route('identify', '/{portal}/rest/services/MapServer/identify')
    config.add_route('find', '/{portal}/rest/services/MapServer/find')
    config.add_route('feature', '/{portal}/rest/services/MapServer/{layerId}/{featureId}')
    config.add_route('features_reload', '/{portal}/features_reload')
    config.add_route('search', '/{portal}/rest/services/SearchServer')
    config.add_route('profile_json', '/{portal}/rest/services/profile.json')
    config.add_route('profile_csv', '/{portal}/rest/services/profile.csv')
    config.add_route('height', '/{portal}/rest/services/height')
    config.add_route('feedback', '/{portal}/feedback')
    config.add_route('owschecker_bykvp', '/{portal}/owschecker/bykvp')
    config.add_route('owschecker_form', '/{portal}/owschecker/form')
    config.add_route('qrcodegenerator', '/{portal}/qrcodegenerator')
    config.add_route('checker', '/{portal}/checker')
    config.add_route('files_collection', '/{portal}/files')
    config.add_route('files', '/{portal}/files/{id}')
    config.add_route('adminkml', '/{portal}/admin/kml')

    # Shortener
    config.add_route('shorten', '/{portal}/shorten.json')
    config.add_route('shorten_redirect', '/{portal}/shorten/{id}')

    # Customer views
    register_customer_view(config)

    # static view definitions
    config.add_static_view('static', 'chsdi:static')
    config.add_static_view('images', 'chsdi:static/images')
    config.add_static_view('examples', 'chsdi:static/doc/examples')
    config.add_static_view('vectorStyles', 'chsdi:static/vectorStyles')
    # keep this the last one
    config.add_static_view('/', 'chsdi:static/doc/build')

    # required to find code decorated by view_config
    config.scan(ignore=['chsdi.tests', 'chsdi.models.vector'])
    return config.make_wsgi_app()
