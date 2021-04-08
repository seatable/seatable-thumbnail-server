#!/bin/bash
source /opt/dockerenv
domain=$SEATABLE_THUMBNAIL_SERVER_HOSTNAME

mkdir -p /var/www/challenges/

python3 /scripts/acme-tiny-master/acme_tiny.py --account-key /opt/ssl/${domain}.account.key --csr /opt/ssl/${domain}.csr --acme-dir /var/www/challenges/ > /opt/ssl/${domain}.crt.tmp || exit
mv /opt/ssl/${domain}.crt.tmp /opt/ssl/${domain}.crt
nginx -s reload
