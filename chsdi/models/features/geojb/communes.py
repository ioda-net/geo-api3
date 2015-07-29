from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import BigInteger
from sqlalchemy import Text


Base = bases['sit']


class Communes(Base, Feature):
    __tablename__ = 'geojb_communes'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'COMMUNES'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    nom = Column(Text(440))
    ofs = Column(BigInteger())
    ofs_arr = Column(BigInteger())


register('geojb', 'COMMUNES', Communes)

