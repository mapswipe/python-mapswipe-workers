# Server Setup

## Lets Encrypt

Install certbot:

```bash
apt-get install certbot
```


Create certificates:

```bash
certbot certonly --standalone
```


Enable and start certbot systemd timer for renewal of certificates:

```bash
systemctl enable certbot.timer
systemctl start certbot.timer
# To check if certbot.timer is enabled run:
systemctl list-units --type timer | grep certbot
```


Add renewal post hook to reload nginx after certificate renwal:

```bash
mkdir -p /etc/letsencrypt/renewal-hooks/deploy
cat <<EOM >/etc/letsencrypt/renewal-hooks/deploy/nginx
#!/usr/bin/env bash

docker container restart nginx
EOM
chmod +x /etc/letsencrypt/renewal-hooks/deploy/nginx
```
