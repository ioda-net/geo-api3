from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text


Base = bases['sit']


class PdzSuperposition(Base, Feature):
    __tablename__ = 'geojb_pdzsuperposition'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'PDZ_SUPERPOSITION'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    texte = Column(Text(30))


register('geojb', 'PDZ_SUPERPOSITION', PdzSuperposition)
