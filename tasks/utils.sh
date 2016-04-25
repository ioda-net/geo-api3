#!/usr/bin/env bash


HELP['venv']="manuel venv

Create a virtual env for the API in .venv"
function venv {
    if [[ ! -d .venv ]]; then
        "virtualenv-${PYTHON_VERSION}" .venv
        "${PIP}" install -U pip
	"${PIP}" install Cython
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
    declare -a ini_files=(production.ini development.ini)
    for file in ${ini_files[@]}; do
        python3 tasks/config.py | "${JINJA2}" --format json \
                    -Dinstall_directory="$(pwd)" \
                    "${file}.jinja2" > "${file}"
    done
}


HELP['wsgi-files']="manuel wsgi-files

Regenetare apache's wsgi-files from the configuration."
function wsgi-files {
    ini-files
    declare -a wsgi_files=(production.wsgi development.wsgi)
    for file in ${wsgi_files[@]}; do
        python3 tasks/config.py | "${JINJA2}" --format json \
                    -Dini_path="$(pwd)/${file%%.*}.ini" \
                    parts/geo-api3.wsgi.jinja2 > "parts/wsgi/${file}"
    done
}