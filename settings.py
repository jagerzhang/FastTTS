from os import getenv
from fastflyer.settings import BaseConfig


class CustomConfig(BaseConfig):
    """
    自定义配置

    Args:
        BaseConfig (_type_): 框架默认配置
    """

    # 修改项目标题
    API_TITLE = "FastTTS"
    # 其他变量请参考BaseConfig内容
    PREFIX = getenv("flyer_base_url", "/speech")
    DESCRIPTION = "<br>".join(
        (
            "**中文名称**：FastTTS 语音合成服务",
            "**功能说明**：基于 edge-tts 的语音合成服务，可以将文字合成为语音文件或文件流，支持和源阅读（legado）无缝对接。",
            "**框架源码**：[Git](https://github.com/jagerzhang/fastflyer)",
            f"**接口文档**：[ReDoc]({PREFIX}/redoc)",
            f"**快速上手**：[SwaggerUI]({PREFIX}/docs)",
            f"**最新发布**：{BaseConfig.RELEASE_DATE}",
        )
    )
