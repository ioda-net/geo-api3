# -*- coding: utf-8 -*-

from chsdi.models import bases
from chsdi.models import register
from chsdi.models.vector import Vector
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import BigInteger
from sqlalchemy import Text


Base = bases['sit']


class BATIMENTS(Base, Vector):
    __tablename__ = 'batiments'
    __table_args__ = ({'schema': 'vector', 'autoload': False})
    __template__ = 'templates/htmlpopup/batiments.mako'
    __bodId__ = 'BATIMENTS'
    id = Column('id', BigInteger, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    commune = Column(Text())
    adresse = Column(Text())
    surface = Column(Float())


register('BATIMENTS', BATIMENTS)
