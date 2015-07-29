from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text


Base = bases['sit']


class CadastreSolaireBis(Base, Feature):
    __tablename__ = 'geojb_cadastresolairebis'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'CADASTRESOLAIREBIS'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    avis = Column(Text(255))
    mail = Column(Text(255))
    url = Column(Text(255))


register('geojb', 'CADASTRESOLAIREBIS', CadastreSolaireBis)
