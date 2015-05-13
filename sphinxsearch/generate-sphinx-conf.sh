#!/usr/bin/env bash

cat sphinx-base.conf db.conf search*.conf > sphinx.conf

if ! indextool --checkconfig -c sphinx.conf > /dev/null 2>&1; then
    indextool --checkconfig -c sphinx.conf
    exit 1
fi
