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
    exit 1
fi
