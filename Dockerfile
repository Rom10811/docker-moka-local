# Base Image
FROM ghcr.io/odoo-it/docker-odoo:14.0 AS base
LABEL maintainer="ivan.todorovich@gmail.com"
# Build Arguments
ARG GITHUB_USER
ARG GITHUB_TOKEN
ARG ODOO_VERSION=14.0
ARG ODOO_SOURCE=OCA/OCB
ARG ODOO_SOURCE_DEPTH=1
# Install Odoo
RUN git clone --single-branch --depth $ODOO_SOURCE_DEPTH --branch $ODOO_VERSION https://github.com/$ODOO_SOURCE $SOURCES/odoo
RUN $RESOURCES/entrypoint.d/100-pip-install-odoo
# Additional configs
COPY conf.d/* $RESOURCES/conf.d/
# Install modules
COPY repos.d $RESOURCES/repos.d
COPY requirements.txt $RESOURCES/requirements.txt
RUN autoaggregate --directory $RESOURCES/repos.d --install --user --output $SOURCES/repositories
RUN pip install --user --no-cache-dir -r $RESOURCES/requirements.txt
