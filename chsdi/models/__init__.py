from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config


# Each string in this type must be the name of a SQLAlchemy driver. You can access a driver
# with engine.driver
PARTIALLY_SUPPORTED_DATABASE_TYPE = ('pysqlite',)
dbs = ['sit']

engines = {}
bases = {}
registered_features = {}

for db in dbs:
    bases[db] = declarative_base()


def initialize_sql(settings):
    for db in dbs:
        if settings['sqlalchemy.sit.url'].startswith('sqlite://'):
            kwargs = {}
        else:
            kwargs = {
                'pool_recycle': 20,
                'pool_size': 20,
                'max_overflow': -1,
            }
        engine = engine_from_config(
            settings,
            'sqlalchemy.%s.' % db,
            **kwargs
        )
        engines[db] = engine
        bases[db].metadata.bind = engine
        bases[db].metadata.info['type'] = engine.driver


def feature_model_from_name(portal_name, layer_name):
    if portal_name in registered_features:
        if layer_name in registered_features[portal_name]:
            return registered_features[portal_name][layer_name]
