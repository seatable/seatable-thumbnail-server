#!/bin/bash

function stop_server() {
    pkill -9 -f seaf-server
    pkill -9 -f uvicorn
    pkill -9 -f multiprocessing

    pkill -9 -f monitor

    rm -f /opt/seatable-thumbnail/pids/*.pid
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

function run_python_wth_env() {
    set_env
    python3 ${*:2}
}

function check_folder() {
    if [[ ! -e /opt/seatable-thumbnail/conf ]]; then
        echo 'do not find /opt/seatable-thumbnail/conf path'
        exit 1
    fi
}

function start_server() {

    check_folder

    stop_server
    sleep 0.5

    set_env

    seaf-server -F /opt/seatable-thumbnail/conf -c /opt/seatable-thumbnail/ccnet -d /opt/seatable-thumbnail/seafile-data -l /opt/seatable-thumbnail/logs/seafile.log -L /opt/seatable-thumbnail -P /opt/seatable-thumbnail/pids/seafile.pid - &
    sleep 0.2

    cd /opt/seatable-thumbnail/seatable-thumbnail-server/
    uvicorn main:app --host 127.0.0.1 --port 8088 --workers 4 --access-log --proxy-headers &>> /opt/seatable-thumbnail/logs/seatable-thumbnail.log &
    sleep 0.2

    /scripts/monitor.sh &>> /opt/seatable-thumbnail/logs/monitor.log &

    echo "SeaTable-thumbnail-server started"
    echo

}


function init() {
    if [[ ! -e /opt/seatable-thumbnail/conf ]]; then
        mkdir /opt/seatable-thumbnail/conf
    fi

    set_env

    python3 /scripts/init_config.py

}

case $1 in
"start")
    start_server
    ;;
"python-env")
    run_python_wth_env "$@"
    ;;
"stop")
    stop_server
    ;;
"init")
    init
    ;;
*)
    start_server
    ;;
esac
