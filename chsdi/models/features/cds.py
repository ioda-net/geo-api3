from sqlalchemy import Column, Text, Integer
from geoalchemy2.types import Geometry

from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature


Base = bases['sit']


class CDS(Base, Feature):
    __tablename__ = 'cds'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'COUVERTUREDUSOL'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                               dimension=2, srid=21781))
    nom = Column(Text(440))
    genre_fr = Column(Text(100))
    genre_de = Column(Text(100))


register('COUVERTUREDUSOL', CDS)
