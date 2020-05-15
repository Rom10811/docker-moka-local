#!/bin/bash

CONF=/opt/odoo/odoo.conf
ODOOCMD="python3 /opt/odoo/OCB/odoo-bin --config $CONF --load=web,muk_saas_branding"

# Configuration generation and Odoo launch
bash genconf.sh && \
  echo "database_manager_system_name = Moka
database_manager_system_logo_url = https://www.mokatourisme.fr/web/image/res.company/1/logo
database_manager_system_favicon_url = https://www.mokatourisme.fr/web/image/website/1/favicon/
database_manager_privacy_policy_url = https://www.mokatourisme.fr/conditions-utilisation" >> /opt/odoo/odoo.conf &&
  $ODOOCMD
