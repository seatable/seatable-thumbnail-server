#!/bin/bash

set -e

# check folder
if [[ ! -e /shared ]]; then
    echo 'do not find /shared path'
    exit 1
fi

if [[ ! -e /shared/nginx-logs ]]; then
    mkdir /shared/nginx-logs
fi

if [[ ! -e /shared/ssl ]]; then
    mkdir /shared/ssl
fi

if [[ ! -e /shared/seatable-thumbnail ]]; then
    mkdir /shared/seatable-thumbnail
fi

if [[ ! -e /shared/seatable-thumbnail/conf ]]; then
    mkdir /shared/seatable-thumbnail/conf
fi

if [[ ! -e /shared/seatable-thumbnail/ccnet ]]; then
    mkdir /shared/seatable-thumbnail/ccnet
fi

if [[ ! -e /shared/seatable-thumbnail/seafile-data ]]; then
    mkdir /shared/seatable-thumbnail/seafile-data
fi

if [[ ! -e /shared/seatable-thumbnail/thumbnail ]]; then
    mkdir /shared/seatable-thumbnail/thumbnail
fi

if [[ ! -e /shared/seatable-thumbnail/pids ]]; then
    mkdir /shared/seatable-thumbnail/pids
fi

if [[ ! -e /shared/seatable-thumbnail/logs ]]; then
    mkdir /shared/seatable-thumbnail/logs
fi

# seatable.sh
if [[ ! -e /shared/seatable-thumbnail/scripts ]]; then
    mkdir /shared/seatable-thumbnail/scripts
fi

if [[ -f /shared/seatable-thumbnail/scripts/seatable-thumbnail.sh ]]; then
    cp /shared/seatable-thumbnail/scripts/seatable-thumbnail.sh /shared/seatable-thumbnail/scripts/seatable-thumbnail.sh.bak
fi

cp /scripts/seatable-thumbnail.sh /shared/seatable-thumbnail/scripts/seatable-thumbnail.sh
sed -i '$a\PATH=/opt/seatable-thumbnail/scripts:$PATH' ~/.bashrc
chmod u+x /shared/seatable-thumbnail/scripts/*.sh

# main
ln -sfn /shared/seatable-thumbnail/* /opt/seatable-thumbnail
ln -sfn /shared/nginx-logs /opt
ln -sfn /shared/ssl /opt
