# Moka docker image

This repo aims to produce docker image used on test
and production server and some utilities to quickly
bring new developers.

# Documentation

https://github.com/odoo-it/docker-odoo#readme


# Possible locale usage

You feel it's easier to develop without docker because
you needs to figure out what's happen in odoo code source
or just because you want to, here a possible path to follow.
## Pre-requisites

* PostgreSQL available on your computer

* Package dependencies as in the base docker image defined in the current [Docker image](./Dockerfile#L1)

* Create a virtualenv env using the same python version as
  in the [Docker based image definition](./Dockerfile) which as today
  is based on [odoo-it/docker-odoo Dockerfile image](https://github.com/odoo-it/docker-odoo/blob/15.0-imp/15.0.Dockerfile)
  (PV to setup the same env as the docker dile, I'm using
  [pyenv](https://github.com/pyenv/pyenv) with 
  [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv))

* install git-aggregator and pre-commit python package

* properly configure your odoo.cfg addons according your installation

### get repos and odoo installed

Create a `custom_code/.env` file that configure repos variable

```env
REPOS_CONFIG_DIR=../repos.test.d
GITHUB_TOKEN="CHANGE_ME"
GITHUB_USER="bot-moka"
ODOO_VERSION=15.0
```

Clone git repos in desired configuration:

```bash
$ git clone --single-branch git@github.com:oca/ocb -b 15.0 ./ocb
$ pip install -r ocb/requirements.txt
$ pip install -e ./ocb
$ cd custom_code/
./custom_code$ for repo_file in `ls ${REPOS_CONFIG_DIR:-../repos.test.d}/*.yml`; do gitaggregate -f --env-file .env -e -j 2 -c $repo_file ; done
```

To avoid to maintain a long list of path in your odoo.cfg to
each repo, you could create a directory with symlink each modules::

```bash
for dir in `find ../custom_code/*/ -maxdepth 1 -mindepth 1 -type d -not -path "**github" -not -path "**.git" -not -path "**setup"`; do ln -s $dir; done
```

so your `odoo.cfg` file `path` looks like:

```conf
addons_path = ./dev_addons/,./ocb/odoo/addons,./ocb/addons
```

And install repo python dependencies

```bash
for reqf in `ls custom_code/*/requirements.txt`; do pip install -r $reqf; done
``
