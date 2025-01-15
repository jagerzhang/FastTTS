# -*- coding: utf-8 -*-
"""
参数定义
"""
from pydantic import BaseModel, Field


class TTSBaseRequest(BaseModel):
    """TTS请求"""

    voice: str = Field(
        "zh-CN-YunxiNeural",
        title="指定语音发音人",
        description="指明使用哪种语音和风格的发音人，例如zh-CN-YunxiNatural。注：可以通过【获取所有语音列表接口】查看更多的语音和风格。",
        embed=True,
    )
    volume: str = Field("+0%", title="朗读音量", description="调整音量，例如+10% ，声音提高了10%", embed=True)
    pitch: str = Field("+0Hz", title="朗读音调", description="调整音调，例如 +1Hz ，音调提高了1Hz", embed=True)


class TTSFullRequest(TTSBaseRequest):
    """TTS请求"""

    text: str = Field("你好, 欢迎访问飞鸽语音合成接口！", title="需要朗读的文本内容", embed=True)
    rate: str = Field("+0%", title="朗读语速", description="调整语速，例如-50%，慢速了50%", embed=True)
