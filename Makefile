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
	@echo "- venv: install deps in a venv"
	@echo "- clean"
	@echo "- serve"
	@echo "- test"
	@echo "- translate"


.PHONY: venv
venv: requirements.txt setup.py
	virtualenv .venv
	${PYTHON_CMD} setup.py develop


.PHONY: serve
serve:
	PYTHONPATH=${PYTHONPATH} ${PSERVE_CMD} development.ini --reload


.PHONY: test
test:
	PYTHONPATH=${PYTHONPATH} ${NOSE_CMD}


.PHONY: lint
lint:
	./lint.sh


.PHONY: translate
translate:
	./translate.sh


.PHONY: clean
clean:
	rm -rf .venv
