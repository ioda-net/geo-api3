PYTHON_CMD ?= $(shell pwd)/.venv/bin/python
PIP_CMD ?= $(shell pwd)/.venv/bin/pip
PSERVE_CMD ?= $(shell pwd)/.venv/bin/pserve
NOSE_CMD ?= $(shell pwd)/.venv/bin/nosetests
PEP8_CMD=$(shell pwd)/.venv/bin/pep8
PYFLAKE_CMD=$(shell pwd)/.venv/bin/pyflakes
# We need GDAL which is hard to install in a venv, modify PYTHONPATH to use the
# system wide version.
PYTHON_VERSION := $(shell python3 --version 2>&1 | cut -d ' ' -f 2 | cut -d '.' -f 1,2)
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
	@echo "- wsgi"
	@echo "- lint"
	@echo "- gdal: install python 3 binding for the gdal"
	@echo "- release: tag the current commit and push it"
	@echo "- prod: update git repo and go to last tag"
	@echo "- revert: revert to the previous tag"


.PHONY: serve
serve: development.ini venv node_modules
	PYTHONPATH=${PYTHONPATH} ${PSERVE_CMD} development.ini --reload

development.ini: node_modules
	@if [ ! -e production.ini ] || [ ! -e development.ini ]; then \
	    cd bin && ./node_modules/gulp/bin/gulp.js build-config; \
	fi

venv:
	# Install Cython before any deps as some need it to compile with
	# optimizations
	@if [ ! -d .venv ]; then \
	    virtualenv-${PYTHON_VERSION} .venv; \
	    ${PIP_CMD} install -U pip; \
	    ${PIP_CMD} install Cython; \
	    ${PYTHON_CMD} setup.py develop; \
	fi

node_modules:
	@if [ ! -d bin/node_modules ]; then \
	    cd bin && npm install; \
	fi


.PHONY: test
test: venv
	PYTHONPATH=${PYTHONPATH} ${NOSE_CMD} --cover-html


.PHONY: lint
lint: pep pyflakes

pep8:
	${PEP8_CMD} --max-line-length 99 chsdi

pyflakes:
	${PYFLAKE_CMD} chsdi


.PHONY: wsgi development.ini
wsgi: node_modules venv
	cd bin && ./node_modules/gulp/bin/gulp.js wsgi


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
	rm -rf production.ini
	rm -rf development.ini


.PHONY: cleanall
cleanall: clean
	rm -rf .venv
	rm -rf bin/node_modules
