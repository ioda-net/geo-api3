#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import os
import sys
import json

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
    BodLayerDe,
    BodLayerFr,
    BodLayerEn,
)


METADATA_TABLES = {
    'view_bod_layer_info_en': BodLayerEn,
    'view_bod_layer_info_fr': BodLayerFr,
    'view_bod_layer_info_de': BodLayerDe
}
TOPIC = 'geojb'


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
    engine = engine_from_config(settings, 'sqlalchemy.sit.')

    create_schema(engine, 'api3')
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
    background_layer_ids = [layer_id.strip()
                            for layer_id in config.get('initdb', 'background_layer_ids').split(',')]

    add_topics(session, background_layer_ids)
    add_layers_config(session, background_layer_ids, config)
    add_catalog(session)

    session.commit()


def add_topics(session, background_layer_ids):
    geojb = Topics(
        id=TOPIC,
        orderKey=0,
        availableLangs='fr,de,en',
        selectedLayers=[],
        backgroundLayers=background_layer_ids,
        showCatalog=True
    )
    api = Topics(
        id='api', orderKey=1, availableLangs='fr,de,en', selectedLayers=[],
        backgroundLayers=[], showCatalog=False)
    all = Topics(id='all', backgroundLayers=[], showCatalog=False)
    session.add(geojb)
    session.add(api)
    session.add(all)


def add_layers_config(session, background_layer_ids, config):
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
        attribution = 'Sigeom SA'
        opacity = layer.opaque
        queryable = bool(layer.queryable)
        layer_row = LayersConfig(
            layerBodId=layer_name,
            attribution=attribution,
            background=False,
            hasLegend=has_legend,
            legendUrl=legend,
            format=format,
            type=type,
            opacity=opacity,
            queryable=queryable,
            selectbyrectangle=queryable,
            serverLayerName=layer_name,
            wmsLayers=layer_name,
            wmsUrl=wms_url,
            maps='{}, {}, {}'.format(TOPIC, 'all', 'api')
        )
        if layer_name in background_layer_ids:
            layer_row.background = True
        session.add(layer_row)
    add_complementary_layers(session)
    add_layers_metadata(session, wms.contents.keys())


def add_complementary_layers(session):
    with open('complementary_layers.json') as complementary_layers_file:
        complementary_layers = json.load(complementary_layers_file)
    for layer_params in complementary_layers.values():
        # In current schema, maps must be a text, not an array
        layer_params['maps'] = ', '.join(layer_params['maps'])
        layer = LayersConfig(**layer_params)
        session.add(layer)


def add_layers_metadata(
        session, layer_names, languages=tuple(('fr', 'en', 'de'))):
    table_name_template = 'view_bod_layer_info_{}'
    for layer_name in layer_names:
        for lang in languages:
            table_name = table_name_template.format(lang)
            Table = METADATA_TABLES[table_name]
            metadata = Table(
                layerBodId=layer_name,
                name=layer_name,
                fullName=layer_name,
                dataOwner='Sigeom SA',
                maps='{}, {}, {}'.format(TOPIC, 'all', 'api'),
                chargeable=True
            )
            session.add(metadata)


def add_catalog(session):
    root = Catalog(topic=TOPIC, category='root', depth=0, path='root')
    session.add(root)
    category = Catalog(
        topic=TOPIC, category='cat1', parentId=1, depth=1, path='root',
        selectedOpen=True, layerBodId='cat1',
        nameDe='cat1', nameFr='cat1',
        nameIt='cat1', nameRm='cat1',
        nameEn='cat1')
    session.add(category)
    for layer in session.query(LayersConfig):
        name = layer.layerBodId
        catalog_entry = Catalog(
            parentId=2, topic=TOPIC, category='layer', layerBodId=name,
            nameDe=name, nameFr=name,
            nameIt=name, nameRm=name,
            nameEn=name,
            path='root/cat1/' + name,
            depth=2)
        session.add(catalog_entry)


if __name__ == '__main__':
    main()
