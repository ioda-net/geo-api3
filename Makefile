PYTHON_CMD ?= $(shell pwd)/.venv/bin/python
PIP_CMD ?= $(shell pwd)/.venv/bin/pip
PSERVE_CMD ?= $(shell pwd)/.venv/bin/pserve
NOSE_CMD ?= $(shell pwd)/.venv/bin/nosetests
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
	@echo "- translate"
	@echo "- prod"
	@echo "- lint"
	@echo "- gdal: install python 3 binding for the gdal"


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

.PHONY: clean
clean:
	rm -rf production.ini
	rm -rf development.ini


.PHONY: cleanall
cleanall: clean
	rm -rf .venv
	rm -rf bin/node_modules
