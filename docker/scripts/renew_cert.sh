#!/bin/bash
source /opt/dockerenv
domain=$SEATABLE_THUMBNAIL_SERVER_HOSTNAME

/usr/bin/mkdir -p /var/www/challenges/

/usr/bin/python3 /scripts/acme-tiny-master/acme_tiny.py --account-key /opt/ssl/${domain}.account.key --csr /opt/ssl/${domain}.csr --acme-dir /var/www/challenges/ > /opt/ssl/${domain}.crt.tmp || exit
/usr/bin/mv /opt/ssl/${domain}.crt.tmp /opt/ssl/${domain}.crt
/usr/sbin/nginx -s reload
