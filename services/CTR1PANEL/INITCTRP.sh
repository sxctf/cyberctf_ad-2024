#!/bin/bash

echo "Initial Start service"
cd /home/uctf/services/CTR1PANEL

docker-compose build
docker-compose up -d
docker-compose down
docker-compose up -d

echo "Service started"