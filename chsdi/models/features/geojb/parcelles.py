from chsdi.models import bases
from chsdi.models import register
from chsdi.models.features import Feature
from geoalchemy2.types import Geometry
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Text
from sqlalchemy import BigInteger


Base = bases['sit']


class Parcelles(Base, Feature):
    __tablename__ = 'geojb_parcelles'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    __bodId__ = 'PARCELLE'
    id = Column('gid', Integer, primary_key=True)
    the_geom = Column(Geometry(geometry_type='GEOMETRY',
                      dimension=2, srid=21781))
    nom = Column(Text(440))
    genre_fr = Column(Text(100))
    genre_de = Column(Text(100))
    numero = Column(Text(400))
    egrid = Column(Text(400))
    grudis = Column(Text(440))
    surface_mo = Column(BigInteger())
    surf_bat_part = Column(BigInteger())
    surf_verte_part = Column(BigInteger())
    surf_rev_dur_part = Column(BigInteger())
    surf_champ_pre_part = Column(BigInteger())
    surf_boise_part = Column(BigInteger())
    surf_eau_part = Column(BigInteger())
    surf_foret_part = Column(BigInteger())
    surf_vigne_part = Column(BigInteger())
    surf_autre_part = Column(BigInteger())
    geom_cons = Column(Text(400))
    bureau_cons = Column(Text(400))
    bureau_url = Column(Text(400))
    date_maj = Column(Text(400))


register('geojb', 'PARCELLE', Parcelles)

