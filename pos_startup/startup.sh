#!/bin/bash
echo "Démarrage du point de vente..."

# Ecran 1
echo "Ecran principal..."
--kiosk --new-window --window-position=0,0 --noerrdialogs --disable-translate --disable-features=TranslateUI ${URL} &

# Ecran 2
echo "Afficheur client..."
google-chrome --kiosk --new-window --window-position=1367,0 --noerrdialogs --disable-translate --disable-features=TranslateUI http://localhost:8069/point_of_sale/display &