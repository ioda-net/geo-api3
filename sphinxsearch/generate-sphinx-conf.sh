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
    number_missed_index=$(indextool --checkconfig -c sphinx.conf | grep "^missed index(es)" | wc -l)
    if (( ${number_missed_index} == 0 )); then
        indextool --checkconfig -c sphinx.conf
        exit 1
    fi
fi

chmod 0640 sphinx.conf
su -c "./deploy-sphinx-conf.sh"