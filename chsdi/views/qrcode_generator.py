import qrcode
from io import BytesIO

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response

from chsdi.lib.url_shortener import create_short_url


@view_config(route_name='qrcodegenerator')
def create_qrcode(request):
    short_url = create_short_url(request)
    img = _make_qrcode_img(short_url)
    response = Response(img, content_type='image/png')
    return response


def _make_qrcode_img(url):
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
