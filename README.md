## FastTTS: 简单语音合成服务

## 项目介绍
本项目基于 Edge-TTS 和 FastFlyer 开发框架，可以直接私有化部署提供语音合成服务。

## 框架介绍
FastFlyer 是基于 FastAPI 设计的轻量级 API 开发框架。在 FastAPI 优异特性的基础上集成了一系列开箱即用的组件，包括Redis、MySQL、Kafka等。采用 SDK 接入方式，内置脚手架代码生成等辅助工具，让研发人员只需要专注于业务逻辑的实现，真正开箱即用！

注：更多框架介绍请阅读：[FastFlyer](https://github.com/jagerzhang/fastflyer)

![FastFlyer](logo.png)

## 快速部署

```
docker run --name fasttts -d -p 8080:8080 jagerzhang/fast-tts 
```
成功启动后，访问：`http://<host>:8080/tts/docs` 可以看到页面效果。

## 简单鉴权

```
docker run -d \
    --name fasttts \
    -p 8080:8080 \
    -e flyer_auth_enable=1 \    # 【可选】启用 BasicAuth 鉴权
    -e flyer_auth_user=guest \  # 【可选】BasicAuth 账号 
    -e flyer_auth_pass=guest \  # 【可选】BasicAuth 密码
    jagerzhang/fast-tts 
```

## 二次开发
初次上手，请仔细阅读FastFlyer说明文档：[正式开发](https://github.com/jagerzhang/fastflyer#正式开发)

## 环境变量
项目支持通过七彩石或环境变量来修改各种配置，优先级上七彩石 > 环境变量，详细参数说明请阅读FastFlyer说明文档：[环境变量](https://github.com/jagerzhang/fastflyer#环境变量)

## 如何加入
PR is welcome!
