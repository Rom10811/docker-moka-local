#!/bin/bash

CONF=/opt/odoo/odoo.conf
ODOOCMD="python3 /opt/odoo/OCB/odoo-bin --config $CONF"

# Configuration generation and Odoo launch
bash genconf.sh && $ODOOCMD
