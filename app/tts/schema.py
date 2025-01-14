# -*- coding: utf-8 -*-
"""
参数定义
"""
from pydantic import BaseModel, Field


class DemoRequest(BaseModel):
    """Demo演示：请求参数."""

    text: str = Field("你好, 欢迎访问语音合成接口！", title="文本", embed=True)
    voice: str = Field("zh-CN-YunxiNeural", title="语言参数", embed=True)
    # rate: str = Field("", title="文件名", embed=True)
    # volume: str = Field("", title="文件名", embed=True)
