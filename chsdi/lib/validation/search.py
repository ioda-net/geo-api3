from pyramid.httpexceptions import HTTPBadRequest

from chsdi.lib.helpers import float_raise_nan

MAX_SPHINX_INDEX_LENGTH = 63
MAX_SEARCH_TERMS = 10


class SearchValidation:

    def __init__(self):
        super().__init__()
        self._searchText = None
        self._bbox = None
        self._returnGeometry = None
        self._origins = None
        self._typeInfo = None
        self._limit = None

    @property
    def searchText(self):
        return self._searchText

    @property
    def bbox(self):
        return self._bbox

    @property
    def returnGeometry(self):
        return self._returnGeometry

    @property
    def origins(self):
        return self._origins

    @property
    def typeInfo(self):
        return self._typeInfo

    @property
    def limit(self):
        return self._limit

    @searchText.setter
    def searchText(self, value):
        if value is None:
            raise HTTPBadRequest("Please provide a search text")
        searchTextList = value.split(' ')
        # Remove empty strings
        searchTextList = [searchText for searchText in searchTextList
                          if searchText]
        if len(searchTextList) > MAX_SEARCH_TERMS:
            raise HTTPBadRequest("The searchText parameter can not contain more than 10 words")
        self._searchText = searchTextList

    @bbox.setter
    def bbox(self, value):
        if value is not None and value != '':
            values = value.split(',')
            if len(values) != 4:
                raise HTTPBadRequest("Please provide 4 coordinates in a comma separated list")
            try:
                values = [float_raise_nan(val) for val in values]
            except ValueError:
                raise HTTPBadRequest("Please provide numerical values for the parameter bbox")
            # Swiss extent
            if values[0] >= 420000 and values[1] >= 30000:
                if values[0] < values[1]:
                    raise HTTPBadRequest("The first coordinate must be higher than the second")
            if values[2] >= 420000 and values[3] >= 30000:
                if values[2] < values[3]:
                    raise HTTPBadRequest("The third coordinate must be higher than the fourth")
            self._bbox = values

    @returnGeometry.setter
    def returnGeometry(self, value):
        if value is False or value == 'false':
            self._returnGeometry = False
        else:
            self._returnGeometry = True

    @origins.setter
    def origins(self, value):
        if value is not None:
            self._origins = value.split(',')

    @typeInfo.setter
    def typeInfo(self, value):
        acceptedTypes = ['locations', 'layers', 'featuresearch', 'locations_preview']
        if value is None:
            message = 'Please provide a type parameter. Possible values are {}'\
                .format(', '.join(acceptedTypes))
            raise HTTPBadRequest(message)
        elif value not in acceptedTypes:
            message = 'The type parameter you provided is not valid. Possible values are {}'\
                .format(', '.join(acceptedTypes))
            raise HTTPBadRequest(message)
        self._typeInfo = value

    @limit.setter
    def limit(self, value):
        if value is not None:
            if value.isdigit():
                self._limit = int(value)
            else:
                raise HTTPBadRequest('The limit parameter should be an integer')
