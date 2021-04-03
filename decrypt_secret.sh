#!/bin/sh

# Decrypt the file
echo $OPENSSL_PRIVATE_KEY > github_actions_private.key
openssl rsautl -decrypt -passin pass:$OPENSSL_PASSPHRASE -inkey github_actions_private.key -in test.json.enc -out test_decrypted.json
