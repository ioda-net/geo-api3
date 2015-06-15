# -*- coding: utf-8 -*-

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import engine_from_config


dbs = ['sit']

engines = {}
bases = {}
registered_features = {}

for db in dbs:
    bases[db] = declarative_base()


def register(name, class_name):
    registered_features.setdefault(name, []).append(class_name)


def initialize_sql(settings):
    for db in dbs:
        engine = engine_from_config(
            settings,
            'sqlalchemy.%s.' % db,
            pool_recycle=20,
            pool_size=20,
            max_overflow=-1
        )
        engines[db] = engine
        bases[db].metadata.bind = engine


def models_from_name(name):
    if name in registered_features:
        return registered_features[name]
