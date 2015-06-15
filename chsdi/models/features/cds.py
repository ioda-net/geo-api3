# -*- coding: utf-8 -*-

from sqlalchemy import Column, Text, Float
from geoalchemy2.types import Geometry

from chsdi.models import bases
from chsdi.models.features import Feature


Base = bases['sit']


class CDS(Base, Feature):
    __tablename__ = 'cds'
    __table_args__ = ({'schema': 'feature', 'autoload': False})
    __template__ = 'templates/htmlpopup/cds.mako'
    __bodId__ = 'COUVERTUREDUSOL'
    id = Column('id', Text, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                               dimension=2, srid=21781))
    commune = Column(Text())
    cds = Column(Text())
    surface = Column(Float())
