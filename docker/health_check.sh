#!/bin/bash
cd $(cd $(dirname $0) && pwd)

# 获取web随机监听信息
if [[ -f /var/run/bind ]];then
    port=$(cat /var/run/bind|awk -F ':' '{print $2}')

else
    port=${flyer_port:-8080}
fi

# 组装健康检查url，发起状态码检查
http_code=$(curl -m 3 -o /dev/null -s -w %{http_code} http://127.0.0.1:${port}/health_check)

# 正常的状态码应该是200
if [[ $http_code -ne 200 ]];then
    echo "health check failed, http_code is $http_code, exit 1"
    exit 1
else
    echo "health check success"
fi

# 自动重载释放释放内存
max_memory_usage_rate=${flyer_max_mem_usage_rate:-0.8}

auto_reload() {
    total_mem_usage=$(awk '/total_rss / {print $2}' /sys/fs/cgroup/memory/memory.stat)
    total_mem_limit=$(cat /sys/fs/cgroup/memory/memory.limit_in_bytes)
    mem_usage_rate=$(awk 'BEGIN{printf "%.2f\n",('$total_mem_usage'/'$total_mem_limit')}')
    if [[ $(expr ${mem_usage_rate} \> ${max_memory_usage_rate}) -eq 1 ]];then
        kill -HUP 1
    fi
}

# 是否开启自动释放内存机制
if [[ ${flyer_auto_reload} -eq 1 ]];then
    auto_reload
fi
