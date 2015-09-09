import pyramid.httpexceptions as exc

from pyramid.view import view_config
from shapely.geometry import box, Point

from chsdi.lib.validation.search import SearchValidation
from chsdi.lib.helpers import format_search_text, transformCoordinate
from chsdi.lib.sphinxapi import sphinxapi
from chsdi.lib import mortonspacekey as msk


class Search(SearchValidation):

    LOCATION_LIMIT = 50
    LAYER_LIMIT = 30
    FEATURE_LIMIT = 20

    def __init__(self, request):
        super().__init__()
        self.quadtree = msk.QuadTree(
            msk.BBox(420000, 30000, 900000, 510000), 20)
        self.sphinx = sphinxapi.SphinxClient()
        self.sphinx.SetServer(request.registry.settings['sphinxhost'], request.registry.settings['sphinxport'])
        self.sphinx.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)
        self.portalName = request.matchdict.get('map')
        self.cbName = request.params.get('callback')
        self.bbox = request.params.get('bbox')
        self.lang = request.params.get('lang')
        self.returnGeometry = request.params.get('returnGeometry', 'true').lower() == 'true'
        self.quadindex = None
        self.origins = request.params.get('origins')
        self.featureIndexes = request.params.get('features')
        self.timeEnabled = request.params.get('timeEnabled')
        self.timeStamps = request.params.get('timeStamps')
        self.typeInfo = request.params.get('type')
        self.limit = request.params.get('limit')
        self.results = {'results': []}
        self.request = request
        self.addressOrigins = [origin.strip() for origin in
                               request.registry.settings['search.address_origins'].split(',')]
        originAndRanks = [originRank.split(':') for originRank in
                          request.registry.settings['search.origins_to_ranks'].split(',')
                          if originRank]
        self.originsToRanks = {origin.strip(): int(rank) for origin, rank in originAndRanks}

    @view_config(route_name='search', renderer='jsonp')
    def search(self):
        self.sphinx.SetConnectTimeout(10.0)
        # create a quadindex if the bbox is defined
        if self.bbox is not None and self.typeInfo not in ('layers', 'featuresearch'):
            self._get_quad_index()
        if self.typeInfo == 'layers':
            # search all layers
            self.searchText = format_search_text(
                self.request.params.get('searchText')
            )
            self._layer_search()
        elif self.typeInfo == 'locations' or self.typeInfo == 'locations_preview':
            self.searchText = format_search_text(
                self.request.params.get('searchText', '')
            )
            self._location_search()
        return self.results

    def _location_search(self):
        if len(self.searchText) < 1 and self.bbox is None:
            raise exc.HTTPBadRequest('You must at least provide a bbox or a searchText parameter')
        limit = self.limit if self.limit and self.limit <= self.LOCATION_LIMIT else self.LOCATION_LIMIT
        self.sphinx.SetLimits(0, limit)

        # Define ranking mode
        if self.bbox is not None:
            geoAnchor = self._get_geoanchor_from_bbox()
            self.sphinx.SetGeoAnchor('lat', 'lon', geoAnchor.GetY(), geoAnchor.GetX())
        else:
            self.sphinx.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
            self.sphinx.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, 'rank ASC, weight ASC')

        # Filter by origins if needed
        if self.origins is None:
            self._detect_keywords()
        else:
            self._filter_locations_by_origins()

        searchList = []
        if len(self.searchText) >= 1:
            searchText = self._query_fields('@(detail,ofs_arr,ofs)')
            searchList.append(searchText)

        if self.bbox is not None:
            geomFilter = self._get_quadindex_string()
            searchList.append(geomFilter)

        if len(searchList) == 2:
            searchTextFinal = '(' + searchList[0] + ') & (' + searchList[1] + ')'
        elif len(searchList) == 1:
            searchTextFinal = searchList[0]

        query_results = None
        if len(searchList) != 0:
            try:
                query_results = self.sphinx.Query(searchTextFinal, index='{}_locations'.format(self.portalName))
            except IOError:  # pragma: no cover
                raise exc.HTTPGatewayTimeout()
            query_results = query_results['matches'] if query_results is not None else query_results
        if query_results is not None and len(query_results) > 0:
            self._parse_location_results(query_results)

    def _layer_search(self):
        layerLimit = self.limit if self.limit and self.limit <= self.LAYER_LIMIT else self.LAYER_LIMIT
        self.sphinx.SetLimits(0, layerLimit)
        self.sphinx.SetRankingMode(sphinxapi.SPH_RANK_WORDCOUNT)
        self.sphinx.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, '@weight DESC')
        index_name = '{portal}_layers_{lang}'\
            .format(portal=self.portalName, lang=self.lang)
        searchText = self._query_fields('@(layer,label)')
        try:
            temp = self.sphinx.Query(searchText, index=index_name)
        except IOError:  # pragma: no cover
            raise exc.HTTPGatewayTimeout()
        temp = temp['matches'] if temp is not None else temp
        if temp is not None and len(temp) != 0:
            self.results['results'] += temp

    def _get_quadindex_string(self):
        ''' Recursive and inclusive search through
            quadindex windows. '''
        if self.quadindex is not None:
            buildQuadQuery = lambda x: ''.join(('@geom_quadindex ', x, ' | '))
            if len(self.quadindex) == 1:  # pragma: no cover
                quadSearch = ''.join(('@geom_quadindex ', self.quadindex, '*'))
            else:
                quadSearch = ''.join(('@geom_quadindex ', self.quadindex, '* | '))
                quadSearch += ''.join(
                    buildQuadQuery(self.quadindex[:-x])
                    for x in range(1, len(self.quadindex))
                )[:-len(' | ')]
            return quadSearch
        else:  # pragma: no cover
            return ''

    def _get_geoanchor_from_bbox(self):
        centerX = (self.bbox[2] + self.bbox[0]) / 2
        centerY = (self.bbox[3] + self.bbox[1]) / 2
        wkt = 'POINT(%s %s)' % (centerX, centerY)
        return transformCoordinate(wkt, 21781, 4326)

    def _query_fields(self, fields):
        exact_nondigit_prefix_digit = lambda x: ''.join((x, '*')) if x.isdigit() else x
        prefix_nondigit_exact_digit = lambda x: x if x.isdigit() else ''.join((x, '*'))
        prefix_match_all = lambda x: ''.join((x, '*'))
        infix_nondigit_prefix_digit = lambda x: ''.join((x, '*')) if x.isdigit() else ''.join(('*', x, '*'))

        exactAll = ' '.join(self.searchText)
        exactNonDigitPreDigit = ' '.join(
            map(exact_nondigit_prefix_digit, self.searchText))
        preNonDigitExactDigit = ' '.join(
            map(prefix_nondigit_exact_digit, self.searchText))
        preNonDigitPreDigit = ' '.join(
            map(prefix_match_all, self.searchText))
        infNonDigitPreDigit = ' '.join(
            map(infix_nondigit_prefix_digit, self.searchText))

        finalQuery = ' | '.join((
            '%s "^%s"' % (fields, exactAll),
            '%s "%s"' % (fields, exactAll),
            '%s "%s"~5' % (fields, exactAll),
            '%s "%s"' % (fields, exactNonDigitPreDigit),
            '%s "%s"~5' % (fields, exactNonDigitPreDigit),
            '%s "%s"' % (fields, preNonDigitExactDigit),
            '%s "%s"~5' % (fields, preNonDigitExactDigit),
            '%s "^%s"' % (fields, preNonDigitPreDigit),
            '%s "%s"' % (fields, preNonDigitPreDigit),
            '%s "%s"~5' % (fields, preNonDigitPreDigit),
            '%s "%s"' % (fields, infNonDigitPreDigit),
            '%s "%s"~5' % (fields, infNonDigitPreDigit)
        ))

        return finalQuery

    def _origins_to_ranks(self, origins):
        try:
            ranks = [self.originsToRanks[origin] for origin in origins]
        except KeyError:
            raise exc.HTTPBadRequest('Bad value(s) in parameter origins')
        return ranks

    def _detect_keywords(self):
        if len(self.searchText) > 0:
            PARCEL_KEYWORDS = ('parzelle', 'parcelle', 'parcella', 'parcel')
            ADDRESS_KEYWORDS = ('addresse', 'adresse', 'indirizzo', 'address')
            firstWord = self.searchText[0].lower()
            if firstWord in PARCEL_KEYWORDS:
                # As one cannot apply filters on string attributes, we use the rank information
                self.sphinx.SetFilter('rank', self._origins_to_ranks(['parcels']))
                del self.searchText[0]
            if firstWord in ADDRESS_KEYWORDS:
                self.sphinx.SetFilter('rank', self._origins_to_ranks(['cities', 'streetnames']))
                del self.searchText[0]

    def _filter_locations_by_origins(self):
        ranks = self._origins_to_ranks(self.origins)
        self.sphinx.SetFilter('rank', ranks)

    def _parse_address(self, res):
        if not self.returnGeometry:
            attrs2Del = ['x', 'y', 'lon', 'lat', 'geom_st_box2d']
            res = {key: value for key, value in res.items() if key not in attrs2Del}
            return res
        return res

    def _parse_location_results(self, results):
        nb_address = 0
        for res in results:
            if nb_address < self.LOCATION_LIMIT:
                if not self.bbox or self._bbox_intersection(self.bbox, res['attrs']['geom_st_box2d']):
                    res['attrs'] = self._parse_address(res['attrs'])
                    self.results['results'].append(res)
                    nb_address += 1

    def _get_quad_index(self):
        try:
            quadindex = self.quadtree\
                .bbox_to_morton(
                    msk.BBox(self.bbox[0],
                             self.bbox[1],
                             self.bbox[2],
                             self.bbox[3]))
            self.quadindex = quadindex if quadindex != '' else None
        except ValueError:  # pragma: no cover
            self.quadindex = None

    def _bbox_intersection(self, ref, result):
        def _is_point(bbox):
            if bbox[0] == bbox[2] and bbox[1] == bbox[3]:
                return True
            else:
                return False
        try:
            refbox = box(ref[0], ref[1], ref[2], ref[3]) if not _is_point(ref) else Point(ref[0], ref[1])
            arr = [float(value) for value in result.replace('BOX(', '').replace(')', '')
                      .replace(',', ' ').split(' ')]
            resbox = box(arr[0], arr[1], arr[2], arr[3]) if not _is_point(arr) else Point(arr[0], arr[1])
        except:  # pragma: no cover
            # We bail with True to be conservative and
            # not exclude this geometry from the result
            # set. Only happens if result does not
            # have a bbox
            return True
        return refbox.intersects(resbox)
