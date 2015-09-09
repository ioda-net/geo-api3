import os.path

from pyramid.view import view_config
from pyramid.renderers import render_to_response
from pyramid.httpexceptions import HTTPBadRequest

from ows_checker import _checker as ows_checker


@view_config(route_name='owschecker_bykvp', renderer='json')
def bykvp(request):
        base_url = request.params.get('base_url', "")
        service = request.params.get('service', "")
        version = request.params.get('version', '1.1.1')
        if base_url == "" or service == "":
            raise HTTPBadRequest("Required parameters 'base_url' or 'service' are missing")

        restful = request.params.get('restful', False)
        ssurl = request.params.get('ssurl', "")
        cwd = os.path.join(
            request.registry.settings['install_directory'],
            "ows_checker/settings/")
        c = ows_checker.OWSCheck(
            base_url=base_url,
            service=service,
            version=version,
            auto=True,
            cwd=cwd,
            ssurl=ssurl,
            restful=bool(restful))
        return c.getResultsOverview(aggregate=True)


@view_config(route_name='owschecker_form', renderer='json')
def form(request):
        base_url = request.params.get('base_url', '')
        service = request.params.get('service', 'WMS')
        restful = request.params.get('restful', False)
        ssurl = request.params.get('ssurl', '')
        version = request.params.get('version', '1.1.1')

        if base_url and service:
            cwd = os.path.join(
                request.registry.settings['install_directory'],
                "ows_checker/settings/")
            c = ows_checker.OWSCheck(
                base_url=base_url,
                service=service,
                version=version,
                auto=True,
                cwd=cwd,
                ssurl=ssurl,
                restful=bool(restful))
            results_dict = c.getResultsOverview(aggregate=True)

        else:
            results_dict = None
        return render_to_response('chsdi:templates/owschecker.mako', {
            'results_dict': results_dict,
            'base_url': base_url,
            'service': service,
            'restful': restful,
            'ssurl': ssurl
        })
