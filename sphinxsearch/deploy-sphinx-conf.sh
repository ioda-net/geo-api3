#!/usr/bin/env bash

cp -a sphinx.conf /etc/sphinx/sphinx.conf
chown sphinx:sphinx /etc/sphinx/sphinx.conf
systemctl restart searchd.service
indexer --verbose --rotate --sighup-each --config /etc/sphinx/sphinx.conf --all