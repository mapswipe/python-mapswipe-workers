#!/bin/bash

docker exec -t postgres pg_dump -U mapswipe-workers -d mapswipe | gzip | split -b 100m - mapswipe.sql.gz
