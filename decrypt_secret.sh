#!/bin/sh

# Decrypt the file
openssl enc -aes-256-cbc -d -K $OPENSSL_KEY -iv $OPENSSL_IV -in ci-mapswipe-63a528ed5bb0.json.enc -out mapswipe_workers/serviceAccountKey.json