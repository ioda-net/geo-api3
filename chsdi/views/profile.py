import math
from pyramid.view import view_config

from chsdi.lib.helpers import round
from chsdi.lib.validation.profile import ProfileValidation
from chsdi.lib.raster.georaster import get_raster


class Profile(ProfileValidation):

    def __init__(self, request):
        super().__init__()
        self.linestring = request.params.get('geom')
        self.elevation_models = request.params.get('elevationModels')
        self.nb_points = request.params.get('nbPoints')
        self.ma_offset = request.params.get('offset')
        self.request = request

    @view_config(route_name='profile_json', renderer='jsonp', http_cache=0)
    def json(self):
        self.json = True
        return self._compute_points()

    @view_config(route_name='profile_csv', renderer='csv', http_cache=0)
    def csv(self):
        self.json = False
        return self._compute_points()

    def _compute_points(self):
        """Compute the alt=fct(dist) array and store it in c.points"""
        def factor(x):
            return float(1) / (abs(x) + 1)

        rasters = [get_raster(model) for model in self.elevation_models]

        # Simplify input line with a tolerance of 2 m
        if self.nb_points < len(self.linestring.coords):
            linestring = self.linestring.simplify(12.5)
        else:
            linestring = self.linestring

        coords = self._create_points(linestring.coords, self.nb_points)
        zvalues = {}
        for i in range(0, len(self.elevation_models)):
            zvalues[self.elevation_models[i]] = []
            for j in range(0, len(coords)):
                z = rasters[i].getVal(coords[j][0], coords[j][1])
                zvalues[self.elevation_models[i]].append(z)

        zvalues2 = {}
        for i in range(0, len(self.elevation_models)):
            zvalues2[self.elevation_models[i]] = []
            for j in range(0, len(zvalues[self.elevation_models[i]])):
                s = 0
                d = 0
                if zvalues[self.elevation_models[i]][j] is None:
                    zvalues2[self.elevation_models[i]].append(None)
                    continue
                for k in range(-self.ma_offset, self.ma_offset + 1):
                    p = j + k
                    if p < 0 or p >= len(zvalues[self.elevation_models[i]]):
                        continue
                    if zvalues[self.elevation_models[i]][p] is None:  # pragma: no cover
                        continue
                    s += zvalues[self.elevation_models[i]][p] * factor(k)
                    d += factor(k)
                zvalues2[self.elevation_models[i]].append(s / d)

        dist = 0
        prev_coord = None
        if self.json:
            profile = []
        # If the renderer is a csv file
        else:
            profile = {'headers': ['Distance'], 'rows': []}
            for i in self.elevation_models:
                profile['headers'].append(i)
            profile['headers'].append('Easting')
            profile['headers'].append('Northing')

        for j in range(0, len(coords)):
            if prev_coord is not None:
                dist += self._dist(prev_coord, coords[j])
            alts = {}
            for i in range(0, len(self.elevation_models)):
                if zvalues2[self.elevation_models[i]][j] is not None:
                    alts[self.elevation_models[i]] = self._filter_alt(
                        zvalues2[self.elevation_models[i]][j])
            if len(alts) > 0:
                rounded_dist = self._filter_dist(dist)
                if self.json:
                    profile.append({
                        'alts': alts,
                        'dist': rounded_dist,
                        'easting': self._filter_coordinate(coords[j][0]),
                        'northing': self._filter_coordinate(coords[j][1])
                    })
                # For csv file
                else:
                    temp = [rounded_dist]
                    for i in alts.items():
                        temp.append(i[1])
                    temp.append(self._filter_coordinate(coords[j][0]))
                    temp.append(self._filter_coordinate(coords[j][1]))
                    profile['rows'].append(temp)
            prev_coord = coords[j]
        return profile

    def _dist(self, coord1, coord2):
        """Compute the distance between 2 points"""
        return math.sqrt(math.pow(coord1[0] - coord2[0], 2.0) +
                         math.pow(coord1[1] - coord2[1], 2.0))

    def _create_points(self, coords, nbPoints):
        """
            Add some points in order to reach roughly the asked
            number of points.
        """
        totalLength = 0
        prev_coord = None
        for coord in coords:
            if prev_coord is not None:
                totalLength += self._dist(prev_coord, coord)
            prev_coord = coord

        if totalLength == 0.0:
            return coords

        result = []
        prev_coord = None
        for coord in coords:
            if prev_coord is not None:
                cur_length = self._dist(prev_coord, coord)
                cur_nb_points = int(nbPoints * cur_length / totalLength + 0.5)
                if cur_nb_points < 1:
                    cur_nb_points = 1
                dx = (coord[0] - prev_coord[0]) / float(cur_nb_points)
                dy = (coord[1] - prev_coord[1]) / float(cur_nb_points)
                for i in range(1, cur_nb_points + 1):
                    result.append(
                        [prev_coord[0] + dx * i,
                         prev_coord[1] + dy * i])
            else:
                result.append([coord[0], coord[1]])
            prev_coord = coord
        return result

    def _filter_alt(self, alt):
        if alt is not None and alt > 0.0:
            # 10cm accuracy is enough for altitudes
            return round(alt * 10.0) / 10.0

    def _filter_dist(self, dist):
        # 10cm accuracy is enough for distances
        return round(dist * 10.0) / 10.0

    def _filter_coordinate(self, coords):
        # 1mm accuracy is enough for distances
        return round(coords * 1000.0) / 1000.0
