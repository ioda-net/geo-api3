from sys import maxsize
from collections import OrderedDict
import datetime
import decimal
import pyramid.httpexceptions as exc
from shapely.geometry import asShape
from shapely.geometry import box
from sqlalchemy.sql import func
from sqlalchemy.orm.util import class_mapper
from sqlalchemy.orm.properties import ColumnProperty
from geoalchemy2.types import Geometry
from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape

import geojson
from papyrus.geo_interface import GeoInterface


def getResolution(imageDisplay, mapExtent):
    bounds = mapExtent.bounds
    mapMeterWidth = abs(bounds[0] - bounds[2])
    mapMeterHeight = abs(bounds[1] - bounds[3])
    xRes = mapMeterWidth / imageDisplay[0]
    yRes = mapMeterHeight / imageDisplay[1]
    return max(xRes, yRes)


def getScale(imageDisplay, mapExtent):
    resolution = getResolution(imageDisplay, mapExtent)
    return resolution * 39.37 * imageDisplay[2]


def getToleranceMeters(imageDisplay, mapExtent, tolerance):
    bounds = mapExtent.bounds
    mapMeterWidth = abs(bounds[0] - bounds[2])
    mapMeterHeight = abs(bounds[1] - bounds[3])
    imgPixelWidth = imageDisplay[0]
    imgPixelHeight = imageDisplay[1]

    # Test for null values
    if all((tolerance, imgPixelWidth, mapMeterWidth, imgPixelHeight, mapMeterHeight)):
        toleranceMeters = max(mapMeterWidth / imgPixelWidth, mapMeterHeight / imgPixelHeight) * \
            tolerance
        return toleranceMeters
    return 0.0  # pragma: no cover


class Feature(GeoInterface):
    __minscale__ = 0
    __maxscale__ = maxsize
    __minresolution__ = 0
    __maxresolution__ = maxsize
    attributes = {}

    # Overrides GeoInterface
    def __read__(self):
        id = None
        geom = None
        properties = OrderedDict()

        for p in class_mapper(self.__class__).iterate_properties:
            if isinstance(p, ColumnProperty):
                if len(p.columns) != 1:  # pragma: no cover
                    raise NotImplementedError
                col = p.columns[0]
                val = getattr(self, p.key)
                if col.primary_key:
                    id = val
                elif isinstance(col.type, Geometry) and \
                        col.name == self.geometry_column_to_return().name:
                    if val is not None:
                        if len(val.data) > 1000000:  # pragma: no cover
                            raise exc.HTTPRequestEntityTooLarge(
                                'Feature ID %s: is too large' % self.id)
                        geom = to_shape(val)
                elif not col.foreign_keys and not isinstance(col.type, Geometry):
                    properties[p.key] = val

        properties = self.insertLabel(properties)
        return geojson.Feature(id=id, geometry=geom, properties=properties)

    @property
    def srid(self):  # pragma: no cover
        return self.geometry_column().type.srid

    # Overrides GeoInterface
    @property
    def __geo_interface__(self):
        feature = self.__read__()
        extents = []
        try:
            shape = asShape(feature.geometry)
            extents.append(shape.bounds)
        except:  # pragma: no cover
            pass

        return geojson.Feature(
            id=self.id,
            geometry=feature.geometry,
            bbox=max(extents, key=extentArea) if extents else None,
            properties=feature.properties,
            # For ESRI
            layerBodId=self.__bodId__,
            layerName='',
            featureId=self.id,
            geometryType=feature.type
        )

    @property
    def __interface__(self):
        return {
            "layerBodId": self.__bodId__,
            "layerName": '',
            "featureId": self.id,
            "attributes": self.getAttributes()
        }

    @classmethod
    def geometry_column(cls):
        return cls.__mapper__.columns['the_geom']

    def geometry_column_to_return(cls):
        geomColumnName = cls.__returnedGeometry__ if hasattr(cls, '__returnedGeometry__') \
            else 'the_geom'
        return cls.__mapper__.columns[geomColumnName]

    @classmethod
    def primary_key_column(cls):
        return cls.__mapper__.primary_key[0]

    @classmethod
    def label_column(cls):
        return cls.__mapper__.columns[cls.__label__] if hasattr(cls, '__label__') \
            else cls.__mapper__.primary_key[0]

    @classmethod
    def geom_filter(cls, geometry, geometryType, imageDisplay, mapExtent, tolerance, epsg):
        toleranceMeters = getToleranceMeters(imageDisplay, mapExtent, tolerance)
        scale = None
        resolution = None
        minScale = cls.__minscale__ if hasattr(cls, '__minscale__') else None
        maxScale = cls.__maxscale__ if hasattr(cls, '__maxscale__') else None
        minResolution = cls.__minresolution__ if hasattr(cls, '__minresolution__') else None
        maxResolution = cls.__maxresolution__ if hasattr(cls, '__maxresolution__') else None
        if None not in (minScale, maxScale) and \
                all(val != 0.0 for val in imageDisplay) and mapExtent.area != 0.0:
            scale = getScale(imageDisplay, mapExtent)
        if None not in (minResolution, maxResolution) and \
                all(val != 0.0 for val in imageDisplay) and \
                mapExtent.area != 0.0:
            resolution = getResolution(imageDisplay, mapExtent)
        if (scale is None or (scale > cls.__minscale__ and scale <= cls.__maxscale__)) and \
                (resolution is None or
                    (resolution > cls.__minresolution__ and resolution <= cls.__maxresolution__)):
            geom = esriRest2Shapely(geometry, geometryType)
            wkbGeometry = WKBElement(memoryview(geom.wkb), epsg)
            geomColumn = cls.geometry_column()
            geomFilter = func.ST_DWITHIN(geomColumn, wkbGeometry, toleranceMeters)
            return geomFilter

    @classmethod
    def get_column_by_property_name(cls, columnPropName):
        if columnPropName in cls.__mapper__.columns:
            return cls.__mapper__.columns.get(columnPropName)

    def getOrmColumnsNames(self, excludePkey=True):
        primaryKeyColumn = self.__mapper__.get_property_by_column(self.primary_key_column()).key
        geomColumnKey = self.__mapper__.get_property_by_column(self.geometry_column()).key
        geomColumnToReturnKey = self.__mapper__\
            .get_property_by_column(self.geometry_column_to_return())\
            .key
        if excludePkey:
            keysToExclude = (primaryKeyColumn, geomColumnKey, geomColumnToReturnKey)

        for column in self.__mapper__.columns:
            ormColumnName = self.__mapper__.get_property_by_column(column).key
            if ormColumnName not in keysToExclude:
                yield ormColumnName

    def getAttributes(self, excludePkey=True):
        attributes = {}
        for ormColumnName in self.getOrmColumnsNames(excludePkey=excludePkey):
            attribute = getattr(self, ormColumnName)
            attributes[ormColumnName] = formatAttribute(attribute)
        return self.insertLabel(attributes)

    def insertLabel(self, attributes):
        labelMappedColumnName = self.__mapper__.get_property_by_column(self.label_column()).key
        attributes['label'] = formatAttribute(getattr(self, labelMappedColumnName))
        return attributes


def formatAttribute(attribute):
    if isinstance(attribute, decimal.Decimal):  # pragma: no cover
        return attribute.__float__()
    elif isinstance(attribute, datetime.datetime):  # pragma: no cover
        return attribute.strftime("%d.%m.%Y")
    else:
        return attribute


def esriRest2Shapely(geometry, geometryType):
    try:
        return asShape(geometry)
    except ValueError:  # pragma: no cover
        return geometry


def extentArea(i):
    geom = box(i[0], i[1], i[2], i[3])
    return geom.area
