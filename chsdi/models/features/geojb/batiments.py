from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Float
from sqlalchemy import BigInteger
from sqlalchemy import Text


Base = bases['sit']


class Batiments(Base, Feature):
    __tablename__ = 'geojb_batiments'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'BATIMENTS'
    id = Column('gid', BigInteger, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    adresse = Column(Text(440))
    commune = Column('nom', Text(440))
    surface = Column(Float())
    genre_fr = Column(Text(100))
    genre_de = Column(Text(100))


register('geojb', 'BATIMENTS', Batiments)
