#!/bin/bash
cd $(cd $(dirname $0) && pwd)
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf >/dev/null 2>&1

test -f .env && source .env
bind_host=${flyer_host:-"0.0.0.0"}
bind_port=${flyer_port:-8080}
workers=${flyer_workers:-1}
log_level=${flyer_console_log_level:-debug}
flyer_access_log=${flyer_access_log:-1}
app_dir=${flyer_app_dir:-app}

if [[ $flyer_access_log -eq 1 ]];then
    access_log=--access-log
else
    access_log=--no-access-log
fi

exec uvicorn \
    --reload \
    --host $bind_host \
    --port $bind_port \
    --workers $workers \
    --log-level $log_level \
    $access_log \
    main:$app_dir
