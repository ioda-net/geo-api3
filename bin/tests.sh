#!/usr/bin/env bash

NOSE_CMD="./.venv/bin/nosetests"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
PYTHONPATH=".venv/lib/python${PYTHON_VERSION}/site-packages:/usr/lib64/python${PYTHON_VERSION}/site-packages"

PYTHONPATH=$PYTHONPATH "${NOSE_CMD}" "$@"
