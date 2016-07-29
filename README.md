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


# Launch with UWSGI with unix socket

## Apache configuration

Replace:

```apache
ProxyPass /api http://localhost:9090 connectiontimeout=5 timeout=180
ProxyPAssReverse /api http://localhost:9090
```

By

```apache
<Location /api>
    Options FollowSymLinks Indexes
    SetHandler uwsgi-handler
    uWSGISocket /run/uwsgi/geo-api3.sock
</Location>
```

## uWSGI

In your `/etc/uwsgi.ini`:

```ini
[uwsgi]
pidfile = /run/uwsgi/uwsgi.pid
emperor = /etc/uwsgi.d
stats = /run/uwsgi/stats.sock
emperor-tyrant = true
plugins = python3
```

Adapt your `config.<branchname>.toml` to get something like this in `uwsgi.ini` (generated with `manuel ini-files`):

```ini
[uwsgi]
chmod-socket = 666
chown-socket = uwsgi:uwsgi
chdir = /home/jenselme/Work/geo-api3
home = /home/jenselme/Work/geo-api3/.venv
gid = uwsgi
uid = uwsgi
ini-paste = /home/jenselme/Work/geo-api3/production.ini
master = 1
plugins = python3
processes = 4
pythonpath = .venv/lib/python3.5/site-packages
pythonpath = /usr/lib64/python3.5/site-packages
pythonpath = /home/jenselme/Work/geo-api3
socket = /run/uwsgi/geo-api3.sock
```

**Note on permissions:** your `production.ini` and `uwsgi.ini` must be owned by the user `uwsgi` and by the group `uwsgi`.
