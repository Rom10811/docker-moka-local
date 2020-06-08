#!/bin/bash
echo "Démarrage du point de vente"

# Ecran 1
echo "Ecran principal..."
chromium-browser --window-position=0,0 --noerrdialogs --kiosk --disable-translate --disable-features=TranslateUI ${URL}

# Ecran 2
echo "Afficheur client..."
chromium-browser --window-position=1400,0 --noerrdialogs --kiosk --disable-translate --disable-features=TranslateUI http://localhost:8069/point_of_sale/display