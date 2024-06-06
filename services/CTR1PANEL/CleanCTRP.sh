#!/bin/bash

echo "Start clean..."
echo "Clean Application data"

docker-compose -f compose.yaml down
rm -r db
rm -r logs

docker-compose -f compose.yaml up -d
docker-compose -f compose.yaml down
docker-compose -f compose.yaml up -d

echo "Finish clean..."