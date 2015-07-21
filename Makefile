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
	@echo "- init: install python deps in a venv and get node modules in bin"
	@echo "- clean"
	@echo "- serve"
	@echo "- test"
	@echo "- translate"


.PHONY: init
init: requirements.txt setup.py
	virtualenv .venv
	${PYTHON_CMD} setup.py develop
	cd bin && npm install


.PHONY: serve
serve: development.ini
	PYTHONPATH=${PYTHONPATH} ${PSERVE_CMD} development.ini --reload

development.ini:
	cd bin && ./node_modules/gulp/bin/gulp.js build-config


.PHONY: test
test:
	PYTHONPATH=${PYTHONPATH} ${NOSE_CMD}


.PHONY: lint
lint:
	./bin/lint.sh


.PHONY: translate
translate:
	./bin/translate.sh


.PHONY: clean
clean:
	rm -rf .venv
