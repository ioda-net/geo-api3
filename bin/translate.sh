#!/usr/bin/env bash

PYBABEL_CMD=".venv/bin/pybabel"

for lang in chsdi/locale/*; do
    if [[ -d "${lang}" ]]; then
        lang="${lang##*/}"
        "${PYBABEL_CMD}" compile -d chsdi/locale --locale "${lang}" --domain chsdi
    fi
done
