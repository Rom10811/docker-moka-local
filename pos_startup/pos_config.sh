#!/bin/bash
sudo apt-get update
sudo apt-get install wget

### Install teamviewer
echo "Installation de Teamviewer..."
wget https://download.teamviewer.com/download/linux/teamviewer_amd64.deb
sudo apt-get install ./teamviewer_amd64.deb
sudo teamviewer setup