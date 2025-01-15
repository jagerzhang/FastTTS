# -*- coding: utf-8 -*-
"""
参数定义
"""
from pydantic import Field
from app.speech.schema import TTSBaseRequest


class TTSToolsRequest(TTSBaseRequest):
    """TOOLS请求参数"""

    username: str = Field(default="", example="", title="用户名", description="用户名")
    password: str = Field(default="", example="", title="密码", description="密码")
