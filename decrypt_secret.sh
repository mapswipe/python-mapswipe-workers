#!/bin/sh


mkdir -p ~/.gnupg/
printf "$GPG_KEY" | base64 --decode > private.key
gpg --import private.key
# Decrypt the file
# --batch to prevent interactive command
# --yes to assume "yes" for questions
gpg --quiet --batch --yes --decrypt --passphrase="$GPG_PASSPHRASE" \
--output ./mapswipe_workers/serviceAccountKey.json ci-mapswipe-63a528ed5bb0.json.gpg