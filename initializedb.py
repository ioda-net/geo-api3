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
    initialize_bod(engine)


def initialize_bod(engine):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    config = configparser.ConfigParser()
    config.read('buildout_config.cfg')

    add_topics(session)
    add_layers_config(session, config)
    add_catalog(session)
    session.commit()


def add_topics(session):
    geojb = Topics(id=TOPIC, orderKey=0, availableLangs='fr,de,en', selectedLayers=[],
                        backgroundLayers=['COUVERTUREDUSOL'], showCatalog=True, staging='')
    session.add(geojb)


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
        layer_row = LayersConfig(layerBodId=layer_name, background=False, hasLegend=has_legend,
                            format=format, type=type, opacity=opacity, queryable=queryable,
                            serverLayerName=layer_name, wmsLayers=layer_name, wmsUrl=wms_url)
        if layer_name == 'COUVERTUREDUSOL':
            layer_row.background = True
        session.add(layer_row)


def add_catalog(session):
    root = Catalog(topic=TOPIC, category='root', depth=0, path='root')
    session.add(root)
    for layer in session.query(LayersConfig):
        name = layer.layerBodId
        catalog_entry = Catalog(parentId=1, topic=TOPIC, category='layer', layerBodId=name,
                                    nameDe=name, nameFr=name,
                                    nameIt=name, nameRm=name, nameEn=name, depth=1, path='root/' + name)
        session.add(catalog_entry)


if __name__ == '__main__':
    main()