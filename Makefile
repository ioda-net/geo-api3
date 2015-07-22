PYTHON_CMD ?= .venv/bin/python
PSERVE_CMD ?= .venv/bin/pserve
NOSE_CMD ?= .venv/bin/nosetests
# We need GDAL which is hard to install in a venv, modify PYTHONPATH to use the
# system wide version.
PYTHON_VERSION := $(shell python3 --version | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
PYTHONPATH ?= .venv/lib/python${PYTHON_VERSION}/site-packages:/usr/lib64/python${PYTHON_VERSION}/site-packages

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo "- cleanall"
	@echo "- clean"
	@echo "- serve"
	@echo "- test"
	@echo "- translate"
	@echo "- prod"


.PHONY: serve
serve: development.ini venv node_modules
	PYTHONPATH=${PYTHONPATH} ${PSERVE_CMD} development.ini --reload

development.ini: node_modules
	@if [ ! -e production.ini ] || [ ! -e development.ini ]; then \
	    cd bin && ./node_modules/gulp/bin/gulp.js build-config; \
	fi

venv:
	@if [ ! -d .venv ]; then \
	    python3 -m venv .venv; \
	    ${PYTHON_CMD} setup.py develop; \
	fi

node_modules:
	@if [ ! -d bin/node_modules ]; then \
	    cd bin && npm install; \
	fi


.PHONY: test
test: venv
	PYTHONPATH=${PYTHONPATH} ${NOSE_CMD}


.PHONY: lint
lint:
	./bin/lint.sh


.PHONY: translate
translate: venv
	./bin/translate.sh


.PHONY: prod
prod: node_modules venv
	cd bin && ./node_modules/gulp/bin/gulp.js wsgi


.PHONY: clean
clean:
	rm -rf production.ini
	rm -rf development.ini


.PHONY: cleanall
cleanall: clean
	rm -rf .venv
	rm -rf bin/node_modules
