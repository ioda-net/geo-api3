from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text


Base = bases['sit']


class OdelPoint(Base, Feature):
    __tablename__ = 'geojb_odelpoint'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'ODELPOINT'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    genre_fr = Column(Text(100))
    genre_de = Column(Text(100))
    nom = Column(Text(440))
    nom_odel = Column(Text(100))


register('geojb', 'ODELPOINT', OdelPoint)
