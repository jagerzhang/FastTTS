#!/bin/bash
cd $(cd $(dirname $0) && pwd)

get_cpu_limit()
{
    cfs_quota_us=$(cat /sys/fs/cgroup/cpu/cpu.cfs_quota_us)
    cfs_period_us=$(cat /sys/fs/cgroup/cpu/cpu.cfs_period_us)
    cpu_limit=$(expr ${cfs_quota_us} / ${cfs_period_us})
    if [[ ${cpu_limit} -ne 0 ]];then
        export CPU_LIMIT=${cpu_limit}
    else
        export CPU_LIMIT=0
    fi
}
# 如果存在执行异常则退出脚本
set -e

# desc: 获取本地网卡IP
# usage: get_ip_of_interface [eth0]
get_ip_of_interface()
{
   local iface=${1:-eth0}
   /sbin/ip addr | grep "$iface$" 2>/dev/null | \
   awk -F '[/ ]+' '/inet / {print $3}'
   # 返回grep的状态，可用于判断$iface是否存在
   return ${PIPESTATUS[1]}
}
 
# desc: 在指定范围内随机数字
# usage: get_range_number STARTNUM ENDNUM
get_range_number()
{ 
    min=$1 
    max=$(($2-$min+1)) 
    num=$(cat /dev/urandom | head -n 10 | cksum | awk -F ' ' '{print $1}') 
    echo $(($num%$max+$min)) 
} 
 
# 检查端口是否被系统占用（包括随机端口）
# usage: check_port <PORT>
# 没有被占用： return 0
# 被占用或者参数为空： return 1
check_port()
{
    if [[ -z $1 ]]; then
        return 1
    fi

    if awk -F '[: ]+' -v p="$1" '$4 == sprintf("%04X", p) {exit 1}' /proc/net/tcp; then
        return 0
    else
        return 1
    fi
}
 
# desc: 获取可用随机端口
# usage: get_random_port STARTPORT ENDPORT RETRY_TIMES
get_random_port()
{
    round=0
    start_port=${1:-10001}
    end_port=${2:-19999}
    retry_times=${3:-10000}
  
    rand_port=$(get_range_number ${start_port} ${end_port})
    while ! check_port ${rand_port}; do
        let round+=1
        if [[ ${round} -ge ${retry_times} ]]; then
            echo "${retry_times} retries, no ports available, export port 0"
            rand_port=0
            break
        fi
        rand_port=$(get_range_number ${start_port} ${end_port})
    done
    echo ${rand_port}
}

export HOST=${flyer_host:-0.0.0.0}
if [[ $flyer_polaris_enabled -eq 1 ]];then
    export PORT=${flyer_port:-$(get_random_port)}
else
    export PORT=${flyer_port:-8080}
fi

export flyer_port=${PORT}
export BIND=${HOST}:${PORT}
export WORKER_CONNECTIONS=${flyer_worker_connections:-1000}

# 通过容器CPU限制计算worker数，可以被flyer_workers变量覆盖
get_cpu_limit

if [[ ! -z ${flyer_workers} ]];then
    export WORKERS=${flyer_workers:-1}
elif [[ ${CPU_LIMIT} -ne 0 ]];then
    export WORKERS=$(expr \( ${CPU_LIMIT} \* 2 \) + 1)
else
    export WORKERS=1
fi

export THREADS=$(expr \( ${CPU_LIMIT} \* 4 \) + 1)
export max_requests=$(expr \( ${THREADS} \* 200 \) )
export max_requests=${flyer_max_requests:-${max_requests}}
export max_requests_jitter=${flyer_max_requests_jitter:-${max_requests}}

export GRACEFUL_TIMEOUT=${flyer_graceful_timeout:-10}
export TIMEOUT=${flyer_timeout:-10}
export flyer_threads=${flyer_threads:-${THREADS}}
export KEEPALIVE=${flyer_keepalive:-5}
export LOG_LEVEL=${flyer_console_log_level:-info}

if [[ "${flyer_access_log}" == "1" ]];then
    # 访问日志默认记录到容器标准输出
    export ACCESS_LOGFILE=${flyer_access_logfile:-/dev/stdout}
    export ACCESS_CONFIG="--access-logfile=${ACCESS_LOGFILE}"
fi

if [[ "${flyer_preload}" == "1" ]];then
    export PRELOAD="--preload"
fi

if [[ "${flyer_enable_max_requests}" == "1" ]];then
    export MAX_REQUESTS="--max-requests ${max_requests}"
    export MAX_REQUESTS_JITTER="--max-requests-jitter ${max_requests_jitter}"
fi

echo ${BIND} > /var/run/bind

exec gunicorn main:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --workers ${WORKERS} \
    --bind ${BIND} \
    --graceful-timeout ${GRACEFUL_TIMEOUT} \
    --timeout ${TIMEOUT} \
    --threads ${flyer_threads}  ${MAX_REQUESTS} ${MAX_REQUESTS_JITTER} \
    --keep-alive ${KEEPALIVE} ${RELOAD} ${PRELOAD} \
    --worker-connections=${WORKER_CONNECTIONS} \
    --access-logformat="${ACCESS_LOGFORMAT}" ${ACCESS_CONFIG} \
    --log-level=${LOG_LEVEL} $@
