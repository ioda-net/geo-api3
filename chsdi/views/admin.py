from pyramid.view import view_config

from chsdi.models.utilities import Files


@view_config(route_name='adminkml', renderer='chsdi:templates/adminkml.mako')
def admin_kml(request):
    files = kml_load(request)
    return {
        'files': files,
        'count': len(files),
        'bucket': request.registry.settings.get('api_url')
    }


def kml_load(request):
    fileid = []
    results = request.db.query(Files)\
        .order_by(Files.createtime)
    for f in results:
        fileid.append((f.file_id, f.admin_id, f.createtime))
    return fileid
