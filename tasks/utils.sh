#!/usr/bin/env bash


HELP['venv']="manuel venv

Create a virtual env for the API in .venv"
function venv {
    if [[ ! -d .venv ]]; then
        python3 -m venv .venv
        "${PIP}" install -U pip
        "${PIP}" install Cython
        "${PIP}" install -r requirements.txt
    fi
    develop
}


HELP['develop']="manuel develop

Install geo-api3 for development ('python setup.py develop')."
function develop {
    "${PYTHON}" setup.py develop
}


HELP['ini-files']="manuel ini-files

Regenerate the ini files for pyramid from the configuration."
function ini-files {
    declare -a ini_files=(production.ini development.ini uwsgi.ini)
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    for file in ${ini_files[@]}; do
        python3 tasks/config.py "${current_branch}" | "${JINJA2}" --format json \
                    -Dinstall_directory="$(pwd)" \
                    "${file}.jinja2" > "${file}"
    done
}


HELP['wsgi-files']="manuel wsgi-files

Regenetare apache's wsgi-files from the configuration."
function wsgi-files {
    ini-files
    declare -a wsgi_files=(production.wsgi development.wsgi)
    local current_branch=$(git rev-parse --abbrev-ref HEAD)
    mkdir -p parts/wsgi
    for file in ${wsgi_files[@]}; do
        python3 tasks/config.py "${current_branch}" | "${JINJA2}" --format json \
                    -Dini_path="$(pwd)/${file%%.*}.ini" \
                    parts/geo-api3.wsgi.jinja2 > "parts/wsgi/${file}"
    done
}
