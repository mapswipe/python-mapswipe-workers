#!/bin/bash

wal-g backup-push /var/lib/postgresql/$(postgres -V)/main
