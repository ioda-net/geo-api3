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


class CadastreSolaire(Base, Feature):
    __tablename__ = 'cadastre_solaire'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'CADASTRESOLAIRE'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    rayonnement = Column(Text())
    surface = Column(Float())
    orientation = Column(BigInteger())
    pente = Column(BigInteger())


register('CADASTRESOLAIRE', CadastreSolaire)
