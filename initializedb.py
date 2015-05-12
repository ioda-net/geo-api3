#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import sys

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from sqlalchemy import engine_from_config
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import CreateSchema

from owslib.wms import WebMapService

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from chsdi.models.bod import (
    Base,
    Topics,
    LayersConfig,
    Catalog,
    )


TOPIC = 'cwdev_geojb'


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    engine = engine_from_config(settings, 'sqlalchemy.bod.')

    create_schema(engine, 're3')
    initialize_bod(engine)


def create_schema(engine, schema_name):
    if not schema_exists(engine, schema_name):
        engine.execute(CreateSchema(schema_name))


def schema_exists(engine, schema_name):
    engine.execute("""PREPARE schema_exists(text) AS
        SELECT EXISTS(SELECT 1 FROM information_schema.schemata
        WHERE schema_name = $1)
        """)
    return engine.execute('EXECUTE schema_exists(%s)', (schema_name, ))\
                .fetchone()[0]


def initialize_bod(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    config = configparser.ConfigParser()
    config.read('buildout_config.cfg')

    init_functions(session)
    add_topics(session)
    add_layers_config(session, config)
    add_catalog(session)
    session.commit()


def init_functions(session):
    remove_accent = u"""
-- custom postgres sql function remove_accents
CREATE OR REPLACE FUNCTION public.remove_accents(string character varying)
  RETURNS character varying AS
$BODY$
    DECLARE
        res varchar;
    BEGIN
        res := replace(string, 'ü', 'ue');
        res := replace(res, 'Ü', 'ue');
        res := replace(res, 'ä', 'ae');
        res := replace(res, 'Ä', 'ae');
        res := replace(res, 'ö', 'oe');
        res := replace(res, 'Ö', 'oe');
        res := replace(res, '(', '_');
        res := replace(res, ')', '_');
        res:= translate(res, 'àáâÀÁÂ', 'aaaaaa');
        res:= translate(res, 'èéêëÈÉÊË', 'eeeeeeee');
        res:= translate(res, 'ìíîïÌÍÎÏ', 'iiiiiiii');
        res:= translate(res, 'òóôÒÓÔ', 'oooooo');
        res:= translate(res, 'ùúûÙÚÛ', 'uuuuuu');
        res:= translate(res, 'ç', 'c');
        RETURN trim(lower(res));
    END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
"""
    session.execute(remove_accent)


def add_topics(session):
    geojb = Topics(id=TOPIC, orderKey=0, availableLangs='fr,de,en', selectedLayers=[],
                        backgroundLayers=['COUVERTUREDUSOL'], showCatalog=True, staging='')
    api = Topics(id='api', orderKey=1, availableLangs='fr,de,en', selectedLayers=[],
                        backgroundLayers=[], showCatalog=False)
    all = Topics(id='all', backgroundLayers=[], showCatalog=False)
    session.add(geojb)
    session.add(api)
    session.add(all)


def add_layers_config(session, config):
    wms_url = config.get('initdb', 'wms_url')
    wms_version = config.get('initdb', 'wms_version')
    wms = WebMapService(wms_url, version=wms_version)
    for layer_name, layer in wms.contents.items():
        styles = layer.styles
        try:
            legend = styles['default']['legend']
        except KeyError:
            legend = ''
        has_legend = bool(legend)
        format = 'PNG'
        type = 'wms'
        opacity = layer.opaque
        queryable = bool(layer.queryable)
        layer_row = LayersConfig(layerBodId=layer_name, attribution='Sigeom SA',
                            background=False, hasLegend=has_legend,
                            format=format, type=type, opacity=opacity, queryable=queryable,
                            serverLayerName=layer_name, wmsLayers=layer_name, wmsUrl=wms_url,
                            maps='{}, {}, {}'.format(TOPIC, 'all', 'api'))
        if layer_name == 'COUVERTUREDUSOL':
            layer_row.background = True
        session.add(layer_row)


def add_catalog(session):
    root = Catalog(topic=TOPIC, category='root', depth=0, path='root')
    session.add(root)
    category = Catalog(topic=TOPIC, category='cat1', parentId=1, depth=1, path='root',
                            selectedOpen=True, layerBodId='cat1',
                            nameDe='cat1', nameFr='cat1',
                            nameIt='cat1', nameRm='cat1',
                            nameEn='cat1')
    session.add(category)
    for layer in session.query(LayersConfig):
        name = layer.layerBodId
        catalog_entry = Catalog(parentId=2, topic=TOPIC, category='layer', layerBodId=name,
                                    nameDe=name, nameFr=name,
                                    nameIt=name, nameRm=name,
                                    nameEn=name,
                                    path='root/cat1/' + name,
                                    depth=2)
        session.add(catalog_entry)


if __name__ == '__main__':
    main()