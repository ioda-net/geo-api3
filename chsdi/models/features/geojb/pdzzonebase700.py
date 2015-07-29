from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text


Base = bases['sit']


class PdzZoneBase(Base, Feature):
    __tablename__ = 'geojb_pdzzonebase700'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'PDZ_MOUTIER_ZDB'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    commune = Column(Text(50))
    canton = Column(Text(30))


register('geojb', 'PDZ_MOUTIER_ZDB', PdzZoneBase)
