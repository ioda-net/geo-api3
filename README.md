mf-chsdi3
=========


# Getting started

Checkout the source code:

    git clone https://github.com/ioda-net/geo-api3.git

The build process relies on a Makefile. Templates are generated with gulp by the
nunjucks render. The gulpfile and utility scripts are located in the bin folder.

Each target is detailed in the Makefile. You don't have to install the dependencies, the
Makefile will do this for you if you haven't downloaded them already.

You can customize the build in a copy of `config.dist.toml`. This copy must be
named `config.toml`. This file is written in the
[toml configuration](https://github.com/toml-lang/toml) language. Without this
configuration file, you will not be able to generate the configuration files
from the templates.


# Serve

- Launch pserve with the development configuration: `make serve`


# Test

- To launch all test, use make: `make test`
- To launch only some test, use bin/test.sh:
  `./bin/tests.sh chsdi/tests/integration/test_file_storage.py`. You can pass it as many files and
  options recognized by nose as you want.


# Lint

Use `make lint`.


# Prod

Use `make prod` to generate the wsgi configuration file for apache. This is the
only thing this target does.


# Recommanded hooks

git hooks allow you to launch a script before or after a git command. They are very handy to
automatically perform checks. If the script exits with a non 0 status, the git command will be
aborted. You must write them in the `.git/hooks/` folder in a file following the convention :
<pre|post>-<git-action>. You must not forget to make them executable, eg:
`chmod +x .git/hooks/pre-commit`.

## pre-commit

```shell
make lint || exit 1
```

## pre-push

```shell
make check || exit 1
```
