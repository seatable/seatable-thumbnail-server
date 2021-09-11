#!/bin/bash

function stop_server() {
    pkill -9 -f seaf-server
    pkill -9 -f uvicorn
    pkill -9 -f multiprocessing
}

function set_env() {
    export SRC_DIR=/opt/seatable-thumbnail/
    export LD_LIBRARY_PATH=/opt/seatable-thumbnail/seafile/lib/
    export PYTHONPATH=/opt/seatable-thumbnail/seafile/lib/python3.6/site-packages/:/usr/lib/python3.6/dist-packages:/usr/lib/python3.6/site-packages:/usr/local/lib/python3.6/dist-packages:/usr/local/lib/python3.6/site-packages
    export PATH=/opt/seatable-thumbnail/seafile/bin/:$PATH

    export CCNET_CONF_DIR=/opt/seatable-thumbnail/ccnet
    export SEAFILE_CONF_DIR=/opt/seatable-thumbnail/seafile-data
    export SEAFILE_CENTRAL_CONF_DIR=/opt/seatable-thumbnail/conf
}


function start_server() {

    stop_server
    sleep 0.5

    set_env

    seaf-server -F /opt/seatable-thumbnail/conf -c /opt/seatable-thumbnail/ccnet -d /opt/seatable-thumbnail/seafile-data -l /opt/seatable-thumbnail/logs/seafile.log -L /opt/seatable-thumbnail -P /opt/seatable-thumbnail/pids/seafile.pid - &
    sleep 0.2

    cd /opt/seatable-thumbnail/seatable-thumbnail-server/
    /usr/local/bin/uvicorn main:app --host 127.0.0.1 --port 8088 --workers 4 --access-log --proxy-headers &>> /opt/seatable-thumbnail/logs/seatable-thumbnail.log &
    sleep 0.2

    echo "SeaTable-thumbnail-server started by logrotate"
    echo

}


case $1 in
"start")
    start_server
    ;;
"stop")
    stop_server
    ;;
*)
    start_server
    ;;
esac
