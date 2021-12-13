#!/bin/bash

# log function
function log() {
    local time=$(date +"%F %T")
    echo "$time $1 "
    echo "[$time] $1 " &>> /opt/seatable-thumbnail/logs/init.log
}


# init config
if [ "`ls -A /opt/seatable-thumbnail/conf`" = "" ]; then
    log "Start init"

    /scripts/seatable-thumbnail.sh init &>> /opt/seatable-thumbnail/logs/init.log
else
    log "Conf exists"
fi


# check nginx
while [ 1 ]; do
    process_num=$(ps -ef | grep "/usr/sbin/nginx" | grep -v "grep" | wc -l)
    if [ $process_num -eq 0 ]; then
        log "Waiting Nginx"
        sleep 0.2
    else
        log "Nginx ready"
        break
    fi
done

if [[ ! -L /etc/nginx/sites-enabled/default ]]; then
    ln -s /opt/seatable-thumbnail/conf/nginx.conf /etc/nginx/sites-enabled/default
    nginx -s reload &>> /opt/seatable-thumbnail/logs/init.log
fi


# letsencrypt renew cert 86400*30
if [[ -f /shared/ssl/renew_cert ]]; then
    env > /opt/dockerenv
    sed -i '1,3d' /opt/dockerenv

    cp /shared/ssl/renew_cert /var/spool/cron/crontabs/root
    chmod 600 /var/spool/cron/crontabs/root

    openssl x509 -checkend 2592000 -noout -in /opt/ssl/$SEATABLE_THUMBNAIL_SERVER_HOSTNAME.crt
    if [[ $? != "0" ]]; then
        log "Renew cert"
        /scripts/renew_cert.sh &>> /opt/seatable-thumbnail/logs/init.log
    fi
fi


# logrotate
if [[ -f /var/spool/cron/crontabs/root ]]; then
    cat /scripts/logrotate-conf/logrotate-cron >> /var/spool/cron/crontabs/root
    /usr/bin/crontab /var/spool/cron/crontabs/root
else
    chmod 0644 /scripts/logrotate-conf/logrotate-cron
    /usr/bin/crontab /scripts/logrotate-conf/logrotate-cron
fi


# autorun
echo
echo "Starting SeaTable Thumbnail"
echo

/scripts/seatable-thumbnail.sh start

wait

sleep 1


#
log "This is a idle script (infinite loop) to keep container running."

function cleanup() {
    kill -s SIGTERM $!
    exit 0
}

trap cleanup SIGINT SIGTERM

while [ 1 ]; do
    sleep 60 &
    wait $!
done
