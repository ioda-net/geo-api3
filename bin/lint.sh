#!/usr/bin/env bash

PEP8_CMD=.venv/bin/pep8
PYFLAKE_CMD=.venv/bin/pyflake

FILES=$(find chsdi -name \*.py | grep -v 'chsdi/lib' | grep -v 'chsdi/static' )
FIXME+=$(echo ${FILES} | xargs ${PEP8_CMD} --ignore=E501)
FIXME+=$(echo -e "\n ")
FIXME+=$(echo ${FILES} | xargs ${PYFLAKE_CMD})

if [[ ${FIXME} == *"chsdi"* || ${FIXME} == *"mapproxy"* ]]; then
    echo "$(tput setaf 1)${FIXME}$(tput sgr0)" &&
    echo "You can fix automatically some styling errors using the following command:" &&
    echo ".venv/bin/autopep8 -v -i -a --ignore=E501 <filename>" &&
    exit 1
fi