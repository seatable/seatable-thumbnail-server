#!/bin/bash

export SRC_DIR=/opt/seatable-thumbnail/
export LD_LIBRARY_PATH=/opt/seatable-thumbnail/seafile/lib/
export PYTHONPATH=/opt/seatable-thumbnail/seafile/lib/python3.6/site-packages/:/usr/lib/python3.6/dist-packages:/usr/lib/python3.6/site-packages:/usr/local/lib/python3.6/dist-packages:/usr/local/lib/python3.6/site-packages
export PATH=/opt/seatable-thumbnail/seafile/bin/:$PATH

export CCNET_CONF_DIR=/opt/seatable-thumbnail/ccnet
export SEAFILE_CONF_DIR=/opt/seatable-thumbnail/seafile-data
export SEAFILE_CENTRAL_CONF_DIR=/opt/seatable-thumbnail/conf


# log function
function log() {
    local time=$(date +"%F %T")
    echo "[$time] $1 "
}

# check process number
# $1 : process name
function check_process() {
    if [ -z $1 ]; then
        log "Input parameter is empty."
        return 0
    fi

    process_num=$(ps -ef | grep "$1" | grep -v "grep" | wc -l)
    echo $process_num
}

# monitor
function monitor_ccnet() {
    process_name="ccnet-server"
    check_num=$(check_process $process_name)
    if [ $check_num -eq 0 ]; then
        log "Start $process_name"
        ccnet-server -F /opt/seatable-thumbnail/conf -c /opt/seatable-thumbnail/ccnet -f /opt/seatable-thumbnail/logs/ccnet.log -d -L /opt/seatable-thumbnail -P /opt/seatable-thumbnail/pids/ccnet.pid - &
        sleep 0.2
    fi
}

function monitor_seafile() {
    process_name="seaf-server"
    check_num=$(check_process $process_name)
    if [ $check_num -eq 0 ]; then
        log "Start $process_name"
        seaf-server -F /opt/seatable-thumbnail/conf -c /opt/seatable-thumbnail/ccnet -d /opt/seatable-thumbnail/seafile-data -l /opt/seatable-thumbnail/logs/seafile.log -L /opt/seatable-thumbnail -P /opt/seatable-thumbnail/pids/seafile.pid - &
        sleep 0.2
    fi
}

function monitor_seatable_thumbnail() {
    process_name="uvicorn"
    check_num=$(check_process $process_name)
    if [ $check_num -eq 0 ]; then
        log "Start $process_name"
        pkill -9 -f multiprocessing
        sleep 0.2
        cd /opt/seatable-thumbnail/seatable-thumbnail-server/
        uvicorn main:app --host 127.0.0.1 --port 8088 --workers 4 --access-log --proxy-headers &>> /opt/seatable-thumbnail/logs/seatable-thumbnail.log &
        sleep 0.2
    fi
}


log "Start Monitor"

while [ 1 ]; do
    monitor_ccnet
    monitor_seafile
    monitor_seatable_thumbnail

    sleep 30
done
