from shapely.geometry import asShape
from pyramid.httpexceptions import HTTPBadRequest

from chsdi.esrigeojsonencoder import loads


class MapServiceValidation:

    def __init__(self):
        self._geometry = None
        self._geometryType = None
        self._returnGeometry = None
        self._imageDisplay = None
        self._mapExtent = None
        self._tolerance = None
        self._layers = None
        self._layer = None
        self._searchText = None
        self._searchField = None
        self._contains = None
        self.esriGeometryTypes = (
            'esriGeometryPoint',
            'esriGeometryPolyline',
            'esriGeometryPolygon',
            'esriGeometryEnvelope'
        )

    @property
    def geometry(self):
        return self._geometry

    @property
    def geometryType(self):
        return self._geometryType

    @property
    def returnGeometry(self):
        return self._returnGeometry

    @property
    def imageDisplay(self):
        return self._imageDisplay

    @property
    def mapExtent(self):
        return self._mapExtent

    @property
    def tolerance(self):
        return self._tolerance

    @property
    def layers(self):
        return self._layers

    @property
    def layer(self):
        return self._layer

    @property
    def searchField(self):
        return self._searchField

    @property
    def contains(self):
        return self._contains

    @geometry.setter
    def geometry(self, value):
        if value is None:
            raise HTTPBadRequest('Please provide the parameter geometry  (Required)')
        else:
            try:
                self._geometry = loads(value)
            except ValueError:  # pragma: no cover
                raise HTTPBadRequest('Please provide a valid geometry')

    @geometryType.setter
    def geometryType(self, value):
        if value is None:
            raise HTTPBadRequest('Please provide the parameter geometryType  (Required)')
        if value not in self.esriGeometryTypes:
            raise HTTPBadRequest('Please provide a valid geometry type')
        self._geometryType = value

    @returnGeometry.setter
    def returnGeometry(self, value):
        if not value or value == 'false':
            self._returnGeometry = False
        else:
            self._returnGeometry = True

    @imageDisplay.setter
    def imageDisplay(self, value):
        if value is None:
            raise HTTPBadRequest('Please provide the parameter imageDisplay  (Required)')
        value = value.split(',')
        if len(value) != 3:
            message = 'Please provide the parameter imageDisplay in a comma separated list of 3 '\
                'arguments (width,height,dpi)'
            raise HTTPBadRequest(message)
        try:
            self._imageDisplay = [float(val) for val in value]
        except ValueError:
            raise HTTPBadRequest('Please provide numerical values for the parameter imageDisplay')

    @mapExtent.setter
    def mapExtent(self, value):
        if value is None:
            raise HTTPBadRequest('Please provide the parameter mapExtent  (Required)')
        else:
            try:
                feat = loads(value)
                self._mapExtent = asShape(feat)
            except ValueError:
                raise HTTPBadRequest('Please provide numerical values for the parameter mapExtent')

    @tolerance.setter
    def tolerance(self, value):
        if value is None:
            raise HTTPBadRequest('Please provide the parameter tolerance (Required)')
        try:
            self._tolerance = float(value)
        except ValueError:
            raise HTTPBadRequest('Please provide a float value for the pixel tolerance')

    @layers.setter
    def layers(self, value):
        if value is None:  # pragma: no cover
            raise HTTPBadRequest('Please provide a parameter layers')
        if value == 'all':
            self._layers = value
        else:
            try:
                layers = value.split(':')[1]
                self._layers = layers.split(',')
            except:
                raise HTTPBadRequest('There is an error in the parameter layers')

    @layer.setter
    def layer(self, value):
        if value is None:
            raise HTTPBadRequest('Please provide a parameter layer')
        if len(value.split(',')) > 1:  # pragma: no cover
            raise HTTPBadRequest('You can provide only one layer at a time')
        self._layer = value

    @searchField.setter
    def searchField(self, value):
        if value is None:
            raise HTTPBadRequest('Please provide a searchField')
        if len(value.split(',')) > 1:
            raise HTTPBadRequest('You can provide only one searchField at a time')
        self._searchField = value

    @contains.setter
    def contains(self, value):
        if value is None or value.lower() == 'true':
            self._contains = True
        else:
            self._contains = False
