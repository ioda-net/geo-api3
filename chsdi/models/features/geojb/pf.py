from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text


Base = bases['sit']


class Pf(Base, Feature):
    __tablename__ = 'geojb_pf'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'PFA12,PFP12,PFA3,PFP3'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    genre = Column(Text(440))
    numero = Column(Text(20))
    genre_fr = Column(Text(100))
    genre_de = Column(Text(100))


register('geojb', ['PFA12', 'PFP12', 'PFA3', 'PFP3'], Pf)
