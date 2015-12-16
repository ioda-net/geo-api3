mf-chsdi3
=========


# Getting started

Checkout the source code:

    git clone https://github.com/ioda-net/geo-api3.git

The build process relies on a manuelfile. Templates are generated with jinja2-cli.

Each target is detailed in the Makefile. You don't have to install the dependencies, `manuel venv`
will create a venv and download them for you.

You can customize the build in a copy of `config/config.dist.toml`. This copy must be
named `config/config.toml`. This file is written in the
[toml configuration](https://github.com/toml-lang/toml) language. Without this
configuration file, you will not be able to generate the configuration files
from the templates. The keys used in it, will override any values loaded from
`config/config.dist.toml`.


# Serve

- Launch pserve with the development configuration: `manuel serve`


# Test

- To launch all test, use make: `manuel test`
- To launch only some test, pass the proper argumemnts to `manuel test`:
  `manuel test chsdi/tests/integration/test_file_storage.py`. You can pass it as many files and
  options recognized by nose as you want.


# Lint

Use `manuel lint`.


# Recommanded hooks

git hooks allow you to launch a script before or after a git command. They are very handy to
automatically perform checks. If the script exits with a non 0 status, the git command will be
aborted. You must write them in the `.git/hooks/` folder in a file following the convention :
<pre|post>-<git-action>. You must not forget to make them executable, eg:
`chmod +x .git/hooks/pre-commit`.

## pre-commit

```shell
manuel lint || exit 1
```

## pre-push

```shell
manuel check || exit 1
```
