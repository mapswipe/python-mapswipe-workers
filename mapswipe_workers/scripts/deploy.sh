#!/bin/bash

# Path variables
dataPath='/var/lib/mapswipe_workers/'
configPath='~/.config/mapswipe_workers/'
logPath='~/var/log/mapswipe_workers/'

# Create dirs
sudo mkdir -p $dataPath
sudo mkdir -p $configPath
sudo mkdir -p $logPath

# Change permissions
sudo chown -R $USER:$USER $dataPath
sudo chown -R $USER:$USER $configPath
sudo chown -R $USER:$USER $logPath

# Copy configuration file and serviceAccountKey
cp ../config/configuration.json $configPath/configuration.json
cp ../config/serviceAccountKey.json $configPath/serviceAccountKey.json

# Start docker
systemctl start docker
docker-compose up -d
