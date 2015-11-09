# We need GDAL which is hard to install in a venv, modify PYTHONPATH to use the
# system wide version.
PYTHON_VERSION := $(shell python3 --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1,2)

-include local.mk

PYTHONPATH ?= .venv/lib/python${PYTHON_VERSION}/site-packages:/usr/lib64/python${PYTHON_VERSION}/site-packages
PYTHON_CMD ?= $(shell pwd)/.venv/bin/python
PIP_CMD ?= $(shell pwd)/.venv/bin/pip
PSERVE_CMD ?= $(shell pwd)/.venv/bin/pserve
NOSE_CMD ?= $(shell pwd)/.venv/bin/nosetests
FLAKE8_CMD ?= $(shell pwd)/.venv/bin/flake8
JINJA2_CMD ?= $(shell pwd)/.venv/bin/jinja2

.PHONY: help
help:
	@echo "Usage: make <target>"
	@echo
	@echo "Possible targets:"
	@echo "- cleanall"
	@echo "- clean"
	@echo "- serve"
	@echo "- test"
	@echo "- wsgi"
	@echo "- lint"
	@echo "- check: lint + test"
	@echo "- testprotocol: test the protocols"
	@echo "- checkall: check + testprotocol"
	@echo "- gdal: install python 3 binding for the gdal"
	@echo "- release: tag the current commit and push it"
	@echo "- prod: update git repo and go to last tag"
	@echo "- revert: revert to the previous tag"


.PHONY: serve
serve: ini_files
	PYTHONPATH=${PYTHONPATH} ${PSERVE_CMD} development.ini --reload

ini_files: development.ini production.ini
	$(JINJA2_CMD) --format toml \
	    -Dapp_version="$(shell date +"%s")" \
	    development.ini.jinja2 \
	    config.toml > development.ini
	$(JINJA2_CMD) --format toml \
	    -Dapp_version="$(shell date +"%s")" \
	    -Dinstall_directory="$(shell pwd)" \
	    production.ini.jinja2 \
	    config.toml > production.ini

.PHONY: venv
venv:
	# Install Cython before any deps as some need it to compile with
	# optimizations
	@if [ ! -d .venv ]; then \
	    virtualenv-${PYTHON_VERSION} .venv; \
	    ${PIP_CMD} install -U pip; \
	    ${PIP_CMD} install Cython; \
	    ${PYTHON_CMD} setup.py develop; \
	fi


.PHONY: test
test:
	PYTHONPATH=${PYTHONPATH} ${NOSE_CMD} --ignore-files test_protocol.py --cover-html


.PHONY: lint
lint:
	${FLAKE8_CMD}  --max-line-length 99 --exclude "conf.py" chsdi


.PHONY: check
check: lint test


.PHONY: testprotocol
testprotocol:
	PYTHONPATH=${PYTHONPATH} ${NOSE_CMD} chsdi/tests/integration/test_protocol.py


.PHONY: checkall
checkall: check testprotocol


.PHONY: wsgi
wsgi: ini_files
	mkdir -p parts/wsgi
	$(JINJA2_CMD) --format toml \
	    -Dini_path="$(shell pwd)/production.ini" \
	    parts/geo-api3.wsgi.jinja2 \
	    config.toml > parts/wsgi/production.wsgi
	$(JINJA2_CMD) --format toml \
	    -Dini_path="$(shell pwd)/development.ini" \
	    parts/geo-api3.wsgi.jinja2 \
	    config.toml > parts/wsgi/development.wsgi


.PHONY: gdal
gdal: venv
	cd .venv && \
	mkdir -p build && \
	${PIP_CMD} install --download build GDAL==1.11.2 && \
	cd build && \
	tar -xzf GDAL-1.11.2.tar.gz && \
	cd GDAL-1.11.2 && \
	${PYTHON_CMD} setup.py build_ext --gdal-config=/usr/bin/gdal-config --library-dirs=/usr/lib --include-dirs=/usr/include/gdal && \
	${PYTHON_CMD} setup.py install --root / && \
	cd ../.. && \
	${PYTHON_CMD} -c "from osgeo import gdal; print('GDAL installed'); print(gdal.__version__, gdal.__file__)"


.PHONY: release
release:
	git tag $(shell date +"%Y-%m-%d-%H-%M-%S")
	git push
	git push --tags


.PHONY: prod
prod:
	git pull && git checkout $(shell git tag | sort -nr | head -n 1) && \
	    sudo systemctl restart apache2


.PHONY: revert
revert:
	git pull && git checkout $(shell git tag | sort -nr | head -n 2 | tail -n 1) && \
	    sudo systemctl restart apache2


.PHONY: clean
clean:
	rm -rf *.ini


.PHONY: cleanall
cleanall: clean
	rm -rf .venv
