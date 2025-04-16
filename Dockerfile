FROM jagerzhang/fastflyer:latest
LABEL maintainer="Jagerzhang<im@zhang.ge>"
LABEL description="基于 FastFlyer 开发框架构建的SRE RESTful API 服务."

WORKDIR /fastflyer

# 安装系统自定义依赖
COPY dependences.txt /tmp/
RUN apt-get install $(cat /tmp/dependences.txt | tr "\n" " ") vim -y && \
    apt-get clean

COPY static/ffmpeg /usr/bin/ffmpeg

# 安装应用自定义依赖
ENV flyer_no_auth_path_prefixs=/tools
COPY requirements.txt /tmp/
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt --index-url https://mirrors.cloud.tencent.com/pypi/simple/
COPY . .

RUN pip install --upgrade fastkit fastflyer --index-url https://pypi.tuna.tsinghua.edu.cn/simple/ && \
    sed -i "s/RELEASE_DATE/$(date '+%Y-%m-%d %H:%M')/" docker/docker-entrypoint.sh && \
    chmod +x /fastflyer/docker/docker-entrypoint.sh && \
    mkdir -p logs

ENTRYPOINT ["docker/docker-entrypoint.sh"]

CMD ["./start.sh"]
