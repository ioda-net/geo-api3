PYTHON_CMD ?= .venv/bin/python
PSERVE_CMD ?= .venv/bin/pserve
NOSE_CMD ?= .venv/bin/nosetests
# We need GDAL which is hard to install in a venv, modify PYTHONPATH to use the
# system wide version.
PYTHONPATH ?= .venv/lib/python2.7/site-packages:/usr/lib64/python2.7/site-packages

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


.PHONY: serve
serve: development.ini venv node_modules
	PYTHONPATH=${PYTHONPATH} ${PSERVE_CMD} development.ini --reload

development.ini: node_modules
	@if [ ! -e production.ini ] || [ ! -e development.ini ]; then \
	    cd bin && ./node_modules/gulp/bin/gulp.js build-config; \
	fi

venv:
	@if [ ! -d .venv ]; then \
	    virtualenv .venv; \
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


.PHONY: clean
clean:
	rm -rf production.ini
	rm -rf development.ini


.PHONY: cleanall
cleanall: clean
	rm -rf .venv
	rm -rf bin/node_modules
