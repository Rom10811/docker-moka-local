#!/bin/bash

# Small program, inspired from Yajo's one : https://bitbucket.org/yajo/docker-odoo
# It generates configuration file

CONF=/opt/odoo/odoo.conf
ADDONS_PATH="/opt/odoo/OCB/addons,/opt/odoo/data/addons"

cd extra-addons
for d in */ ; do
  if ! [ "$d" == "*/" ]; then
    ADDONS_PATH="$ADDONS_PATH,/opt/odoo/extra-addons/$d"
  fi
done

cd ../custom-addons
for d in */ ; do
  if ! [ "$d" == "*/" ]; then
    ADDONS_PATH="$ADDONS_PATH,/opt/odoo/custom-addons/$d"
  fi
done

# Configuration generation
echo "
[options]
; Configuration file auto-generated
addons_path = $ADDONS_PATH
data_dir = ${DATA:=/opt/odoo/data}
dbfilter = ${DB_FILTER}
db_name = ${DB_NAME}
db_host = ${DB_HOST:=postgres}
db_port = ${DB_PORT:=5432}
db_user = ${POSTGRES_USER:=odoo}
db_password = $POSTGRES_PASSWORD
db_maxconn = ${DB_MAXCONN:=20}
list_db = ${LIST_DB:=True}
xmlrpc_port = ${XMLRPC_PORT:=8069}
longpolling_port = ${LONGPOLLING_PORT:=8072}
proxy_mode = ${PROXY_MODE:=True}
workers = ${WORKERS:=2}
limit_time_cpu = ${LIMIT_TIME_CPU:=120}
limit_time_real = ${LIMIT_TIME_REAL:=240}
limit_memory_soft = ${LIMIT_MEMORY_SOFT:=2684354560}
limit_memory_hard = ${LIMIT_MEMORY_HARD:=6442450944}
admin_passwd = ${ADMIN_PASSWORD:=admin}" > $CONF
