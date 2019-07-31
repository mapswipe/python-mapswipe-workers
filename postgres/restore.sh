#!/bin/bash

cat mapswipe.sql.gz* | gunzip | docker exec -i postgres psql -U mapswipe -d mapswipe-workers
