#!/usr/bin/env bash

error_exit() {
    echo "$1" >&2
    exit "${2:-1}"
}

cd ..
./deploy.py > /dev/null 2>&1 || error_exit "Failed to generate template"
cd "sphinxsearch"

cat sphinx-base.conf db.conf search*.conf > sphinx.conf

if ! indextool --checkconfig -c sphinx.conf > /dev/null 2>&1; then
    indextool --checkconfig -c sphinx.conf
#   If we have missing indexes we will never
#   create the first configuration
#    exit 1
fi

chmod 0640 sphinx.conf
sudo cp -a sphinx.conf /etc/sphinx/sphinx.conf
sudo chown sphinx:sphinx /etc/sphinx/sphinx.conf
sudo systemctl restart searchd.service

