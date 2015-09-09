from sqlalchemy import inspect
from sqlalchemy import BigInteger
from sqlalchemy import Column
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.schema import MetaData
from sqlalchemy.schema import Table
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import NoResultFound

from chsdi.models import bases
from chsdi.models import engines
from chsdi.models import registered_features
from chsdi.models.features import Feature


Base = bases['sit']


class MapLayersFeatures(Base):
    __tablename__ = 'map_layers_features'
    __table_args__ = ({'schema': 'features', 'autoload': False})
    feature = Column(Text(200), primary_key=True)
    portal_names = Column(ARRAY(Text(200)))
    layer_names = Column(ARRAY(Text(200)))


def register_features():
    for engine in engines.values():
        features_names = _get_feature_names(engine)
        session = Session(bind=engine)
        meta = MetaData(bind=engine, schema='features')
        for feature in features_names:
            try:
                map_layers_features = session.query(MapLayersFeatures)\
                    .filter(MapLayersFeatures.feature == feature)\
                    .one()
            except NoResultFound:
                # We may encounter view that exist but for which the mapping
                # has not been created yet.
                continue
            FeatureModel = _get_feature_model(meta, map_layers_features, feature)
            _register(
                map_layers_features.portal_names,
                map_layers_features.layer_names,
                FeatureModel)


def _get_feature_names(engine):
    insp = inspect(engine)
    return insp.get_view_names(schema='features')


def _get_feature_model(meta, map_layers_features, feature):
    feature_table = Table(
        feature,
        meta,
        Column('gid', BigInteger, primary_key=True, key='id'),
        autoload=True)
    return type(
        feature,
        (Base, Feature),
        {
            '__table__': feature_table,
            '__bodId__': ','.join(map_layers_features.layer_names)
        })


def _register(portal_names, layer_names, feature_class):
    for portal_name in portal_names:
        for layer_name in layer_names:
            registered_features.setdefault(portal_name, {})\
                .setdefault(layer_name, [])\
                .append(feature_class)


register_features()
