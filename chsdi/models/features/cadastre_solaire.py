# -*- coding: utf-8 -*-

from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import Text


Base = bases['sit']


class CADASTRE_SOLAIRE(Base, Feature):
    __tablename__ = 'cadastre_solaire'
    __table_args__ = ({'schema': 'feature', 'autoload': False})
    __template__ = 'templates/htmlpopup/cadastre_solaire.mako'
    __bodId__ = 'CADASTRESOLAIRE'
    id = Column('id', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    rayonnement = Column(Text())
    surface = Column(Float())
    orientation = Column(BigInteger())
    pente = Column(BigInteger())


register('CADASTRESOLAIRE', CADASTRE_SOLAIRE)
