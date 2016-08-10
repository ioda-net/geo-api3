#!/usr/bin/env bash

# We need GDAL which is hard to install in a venv, modify PYTHONPATH to use the
# system wide version.
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
export PYTHONPATH=".venv/lib/python${PYTHON_VERSION}/site-packages:/usr/lib64/python${PYTHON_VERSION}/site-packages:/usr/lib/python${PYTHON_VERSION}/site-packages:$(pwd)"

FLAKE8="$(pwd)/.venv/bin/flake8"
JINJA2="$(pwd)/.venv/bin/jinja2"
NOSE="$(pwd)/.venv/bin/nosetests"
PIP="$(pwd)/.venv/bin/pip"
PSERVE="$(pwd)/.venv/bin/pserve"
PYTHON="$(pwd)/.venv/bin/python"
