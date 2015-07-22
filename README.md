mf-chsdi3
=========


# Getting started

Checkout the source code:

    git clone https://github.com/ioda-net/geo-api3.git

The build process relies on a Makefile. Templates are generated with gulp by the
nunjucks render. The gulpfile and utility scripts are located in the bin folder.

Each target is detailed below. You don't have to install dependencies, the
Makefile will do this for you if you haven't downloaded them already.

You can customize the build in a copy of `config.dist.toml`. This copy must be
named `config.toml`. This file is written in the
[toml configuration](https://github.com/toml-lang/toml) language. Without this
configuration file, you will not be able to generate the configuration files
from the templates.


# Serve

Launch pserve with the development configuration.


# Test

Use nose to launch the tests. Launch all tests by default. Call `.venv/bin/nose`
to launch a test in particular.


# Lint

Use `pep8` to check the respect of the python coding style. More details in the
lint script (`bin/lint.sh`).


# Prod

Use `make prod` to generate the wsgi configuration file for apache. This is the
only thing this target does.