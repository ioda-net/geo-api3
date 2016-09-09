import requests

from io import BytesIO
from urllib.parse import urlparse
from zipfile import ZipFile

from pyramid.view import view_config

from pyramid.httpexceptions import HTTPBadRequest, HTTPBadGateway, HTTPNotAcceptable
from pyramid.response import Response


DEFAULT_ENCODING = 'utf-8'


class OgcProxy:
    def __init__(self, request):
        self.request = request

    @view_config(route_name='ogcproxy')
    def ogcproxy(self):

        url = self.request.params.get("url")
        if url is None:
            return HTTPBadRequest('No URL provided')

        # check for full url
        parsed_url = urlparse(url)
        if not parsed_url.netloc or parsed_url.scheme not in ("http", "https"):  # pragma: no cover
            raise HTTPBadRequest('URL must contain the scheme (http or https)')

        # forward request to target (without Host Header)
        h = dict(self.request.headers)
        h.pop("Host", h)
        try:
            resp = requests.request(self.request.method, url,
                                    data=self.request.body, headers=h,
                                    verify=False)
            content = resp.content
        except:  # pragma: no cover
            raise HTTPBadGateway()

        #  All content types are allowed
        if "content-type" in resp.headers:
            ct = resp.headers["content-type"]
            if ct == "application/vnd.google-earth.kmz":
                zipfile = None
                try:
                    zipfile = ZipFile(BytesIO(content))
                    content = ''
                    kml_files = [filename for filename in zipfile.namelist()
                                 if filename.endswith('.kml')]
                    # Normally we should only have one kml in the kmz
                    if len(kml_files) > 0:
                        kml_file = kml_files[0]
                        content = zipfile.open(kml_file).read()
                        ct = 'application/vnd.google-earth.kml+xml'
                except Exception:  # pragma: no cover
                    raise HTTPBadGateway()
                finally:
                    if zipfile:
                        zipfile.close()
        else:  # pragma: no cover
            raise HTTPNotAcceptable()

        if resp.encoding:
            doc_encoding = resp.encoding
            if doc_encoding.lower() != DEFAULT_ENCODING:
                try:
                    data = content.decode(doc_encoding, "replace")
                except Exception:  # pragma: no cover
                    message = "Cannot decode requested content from advertized encoding: %s into "
                    "unicode." % doc_encoding
                    raise HTTPNotAcceptable(message)
                content = data.encode(DEFAULT_ENCODING)
                content = content.replace(
                    doc_encoding.encode('utf-8'),
                    DEFAULT_ENCODING.encode('utf-8'))

        response = Response(content, status=resp.status_code,
                            headers={"Content-Type": ct})

        return response
