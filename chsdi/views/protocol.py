import requests

from pyramid.view import view_config

from pyramid.httpexceptions import (
    HTTPBadRequest,
    HTTPBadGateway,
    HTTPNotAcceptable,
    HTTPNotFound
)
from pyramid.response import Response


class Protocol:

    def __init__(self, request):
        self.request = request
        self.config = {
          'filename': request.registry.settings['protocol.filename'],
          'pfp': request.registry.settings['protocol.pfp'],
          'geo': request.registry.settings['protocol.geo'],
          'pdc': request.registry.settings['protocol.pdc']
        }

    @view_config(route_name='protocol')
    def protocol(self):
        type = self.request.matchdict['type']
        id = self.request.matchdict['id']

        if type not in self.config:
            raise HTTPNotAcceptable('Invalid type: ' + type)

        url = self.config[type] + id

        try:
            resp = requests.get(url)
            content = resp.content
        except:
            raise HTTPBadGateway()

        if "content-type" in resp.headers:
            ct = resp.headers["content-type"]
            if ct == "application/pdf":
                return Response(content, status=resp.status_code,
                                headers={"Content-Type": ct})
            else:
                raise HTTPNotFound()

        # We should only get pdf response.
        # Anything else is not valid
        raise HTTPNotAcceptable()
