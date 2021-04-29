# Moka docker image

This repo aims to produce docker image used on test
and production server and some utilities to quickly
bring new developers.


## Development

Here we will explore how to install development environment
using two different ways:

* Using docker
* Without docker

Then we will see how to basically setup the database/launch test
and run odoo.

### Docker environment

This methods allow to get an environnent closed
to the running server in production while
it also bring some complexity related to
how docker works.

#### Pre-requisites

* I (PV) usually create a virtualenv env I use docker
  to install docker-compose and pre-commit
  [Local environment](#Local%20environment)


#### Build

build docker images to produce postgresql specific and odoo
images.

```bash
$ docker-compose build
```

The `docker-compose.yml` file describe services and details
build context.

At the time writing this produce 3 images:

* **docker-moka_pgmoka:latest**: Postgresql image with FR local to
  properly manage [Postgresql collation](https://www.postgresql.org/docs/current/collation.html)
* **registry.yaltik.net/odoo:moka12**: This is a base image for `test` and
  `prod` based on [Dockerfile.odoo12](./Dockerfile.odoo12) and contains all common stuff.
* **docker-moka_mokatest:latest**: This image to be use for development environment using
  [Dockerfile.odoo12](./Dockerfile.test).

Build relies on [git-aggregator](https://pypi.org/project/git-aggregator/) to retrieve
git repos and optionally merge branches required for a build.

`git-aggregator` use `repos.<env>.yaml` files as configuration to
define the right version to use. `Dockerfile.<env>` use respective `repos.<env>.yaml`
files.

#### Develop

* Clone repo you needs to develop

Repos that you want to develop should be placed under `./custom_code`
this will properly hide installed in the base image.

Let's say you want to develop a new feature in [moka-depot-vente repo](
https://github.com/Moka-Tourisme/moka-depot-vente)

```bash
mkdir -p ./custom_code
git clone -b 12.0-dev git@github.com:Moka-Tourisme/moka-depot-vente.git ./custom_code/moka-depot-vente
```

or use `gitaggregate` as in local development section to get all repos.

> **Note**: keep in mind that `repo.<env>.yml` mainly reference branch name
> that may move to a different commit between
> your development time and the CI build time which will finally deployed

* Before reading Odoo development you'll have to prefix all your commands with
  ``docker-compose run --rm mokatest`` for instance to get odoo help:

```bash
 docker-compose run --rm mokatest odoo --help
```

You may use an ALIAS if you want ;)

```bash
$ alias odoo='docker-compose run --rm mokatest odoo'
$ odoo -h
```

### Local environment

You feel it's easier to develop without docker because
you needs to figure out what's happen in odoo code source
or just because you want to, here some path I follow.

#### Pre-requisites

* postgresql installed or postgresl docker

* Package dependencies as described in [Docker image definition](./Dockerfile.odoo12#L1)

* Create a virtualenv env using the same python version as
  in the [Docker image definition](./Dockerfile.odoo12#L1)
  (PV I use the same env that I used with docker, I'm using
  [pyenv](https://github.com/pyenv/pyenv) with 
  [pyenv-virtualenv](https://github.com/pyenv/pyenv-virtualenv)
  for that)

* install git-aggregator and pre-commit python package

* properly configure you odoo.cfg addons according your installation

#### get repos and odoo installed

```bash
$ git clone --single-branch git@github.com:oca/ocb -b 12.0 ./ocb
$ pip install -r ocb/requirements.txt
$ pip install -e ./ocb
$ cd custom_code/
./custom_code$ export GODOO_VERSION=12.0
./custom_code$ export GITHUB_USER=<github user>
./custom_code$ export GITHUB_USER=<github token>
./custom_code$ gitaggregate --expand-env -c ../repos.test.yml
```

To avoid to maintain a long list of path in your odoo.cfg to
each repo, you could create a directory with symlinc each modules::

```bash
for dir in `find ../custom_code/*/ -maxdepth 1 -mindepth 1 -type d -not -path "**github" -not -path "**.git" -not -path "**setup"`; do ln -s $dir; done
```


### Odoo development

Here you can find some daily basis commands.

* If you are running the docker version we assume you've set alias as shown above
  or running command inside the mokatest container.
* providing different odoo config file can be done with `-c path/to/odoo.cfg` 

#### Pre-commit

Inside most of repositories you'll get a ``.pre-commit-config.yaml``
file that prevent you to commit ugly things!

It's based on famous [pre-commit](https://pre-commit.com/) which
which relies on [git hooks](https://git-scm.com/docs/githooks)
to execute check right before commit effectively happen.

So you have to install hooks, at the same time you can install
dependence's hooks. In repo you'll develop:

```bash
pre-commit install --install-hooks
```

you can run hooks manually:

```bash
pre-commit run --all-files --show-diff-on-failure
```

> **Note** you can disable hooks for an "draft" commit using
> `git -n` 


#### Create a database with demo data

An example to install moka_depot_vente with demo data:

```bash
odoo -d mokatest -i moka_depot_vente --stop-after-init
```

#### generate/update translation file (.po/.pot)

* First time prepare a translation database with fr_FR loaded

```bash
odoo -d moka-translation -i moka_depot_vente --load-language fr_FR --stop-after-init
```

* install [click-odoo-contrib](https://pypi.org/project/click-odoo-contrib) (`pip install click-odoo-contrib`)
* install `msgmerge` in `gettext` (debian) package

* generate `.pot` file and merge `.po`

```bash
click-odoo-makepot \
  -c odoo.local.conf \
  -d moka-translation \
  --log-level info \
  --addons-dir custom_addons/moka-depot-vente \
  --msgmerge \
  --purge-old-translations \
  --no-fuzzy-matching
```

* make change in translation files
* next time you update your module you'll have to use ``--i18n-overwrite`` to
  get modifications from repo, change done in database directly can be lost 

```bash
odoo -d moka-translation -u moka_depot_vente --i18n-overwrite --stop-after-init
```

#### Launch test using odoo

Launching test using odoo command limited to one module after it's update

```bash
odoo -d moka-test -u moka_depot_vente --test-enable --test-tags /moka_depot_vente --stop-after-init
```


#### Launch test using pytest-odoo

[pytest](https://docs.pytest.org) has a lot of handy commands in order to run only
failed test, integrated with `pytest-cov` you can easly generate coverage files
to explore uncovered code !

assuming you have install you database with demo data

```bash
pip install pytest-odoo pytest-cov
pytest --odoo-database mokatest --odoo-config <path/to/odoo.config.cfg> [usual pytest args]
```

> **Note**: Mind to update your module if you have change in model or data that your test depends.

> **Note**: at install test should probably skipped

#### running odoo

Using docker-compose you have to run `docker-compose up -d after` assuming
you have a database already initialized.

Running dev odoo server is listening `127.0.0.1:8840`.
