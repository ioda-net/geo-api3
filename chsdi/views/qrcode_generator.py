import requests
import json
from io import BytesIO

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from chsdi.lib.helpers import check_url, make_api_url, quoting


@view_config(route_name='qrcodegenerator')
def qrcode(request):

    url = quoting(check_url(
        request.params.get('url'), request.registry.settings
    ))
    url = _shorten_url(request, url)
    img = _make_qrcode_img(url)
    response = Response(img, content_type='image/png')
    return response


def _make_qrcode_img(url):
    import qrcode
    # For a qrcode of 128px
    qr = qrcode.QRCode(
        box_size=4,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        border=3
    )
    try:
        qr.add_data(url)
        qr.make()
        output = BytesIO()
        img = qr.make_image()
        img.save(output)
    except:  # pragma: no cover
        raise HTTPBadRequest('An error occured during the qrcode generation')
    return output.getvalue()


def _shorten_url(request, url):
    API3_SHORTEN_URL = make_api_url(request) + '/shorten.json?url=%s'
    try:
        resp = requests.get(API3_SHORTEN_URL % url)
        resp = json.loads(resp.text)
        url = resp['shorturl']
        return url
    except:  # pragma: no cover
        return url
