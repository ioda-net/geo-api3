# -*- coding: utf-8 -*-

from sqlalchemy import Column, Integer, Text, Float
from geoalchemy2.types import Geometry

from chsdi.models import register, bases
from chsdi.models.vector import Vector


Base = bases['sit']


class CDS(Base, Vector):
    __tablename__ = 'cds'
    __table_args__ = ({'schema': 'vector', 'autoload': False})
    __template__ = 'templates/htmlpopup/cds.mako'
    __bodId__ = 'COUVERTUREDUSOL'
    id = Column('id', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                               dimension=2, srid=21781))
    commune = Column(Text())
    cds = Column(Text())
    surface = Column(Float())


register('COUVERTUREDUSOL', CDS)
