from pydantic import BaseModel, Field, validator, constr, root_validator
import re


class TTSBaseRequest(BaseModel):
    """TTS请求基础参数"""

    voice: str = Field(
        default="zh-CN-YunxiNeural",
        example="zh-CN-YunxiNeural",
        title="指定语音发音人",
        description="指明使用哪种语音和风格的发音人，例如zh-CN-YunxiNatural。注：可以通过【获取所有语音列表接口】查看更多的语音和风格。",
        embed=True,
    )
    volume: str = Field(
        default="+0%", example="+0%", title="朗读音量", description="调整音量，例如+10% ，声音提高了10%", embed=True
    )
    pitch: str = Field(
        default="+0Hz", example="+0Hz", title="朗读音调", description="调整音调，例如 +1Hz ，音调提高了1Hz", embed=True
    )

    @validator("volume", "pitch", pre=True)
    def add_plus_sign(cls, value):
        """如果值没有以 + 或 - 开头，则在前面加上 +"""
        if not value.startswith(("+", "-")):
            return f"+{value}"
        return value


class TTSFullRequest(TTSBaseRequest):
    """TTS请求全量参数"""

    text: constr(min_length=1, max_length=500) = Field(
        ..., example="你好, 欢迎访问飞鸽语音合成接口！", title="需要朗读的文本内容", embed=True
    )
    rate: str = Field(
        default="+0%", example="+0%", title="朗读语速", description="调整语速，例如-50%，慢速了50%", embed=True
    )
    replacement: int = Field(
        default=0,
        example=0,
        title="是否启用文本替换机制",
        description="默认不启用，如果启用，文本内容为空或纯字符校验不通过时将替换文本内容为默认错误信息，规避源阅读APP里面内容无文字导致请求失败",
    )

    @validator("rate", pre=True)
    def add_plus_sign_rate(cls, value):
        """如果值没有以 + 或 - 开头，则在前面加上 +"""
        if not value.startswith(("+", "-")):
            return f"+{value}"
        return value

    @root_validator(pre=True)
    def validate_text(cls, values):
        """校验文本内容"""
        text = values.get("text")
        replacement = values.get("replacement") or 0

        if not text or not text.strip():
            if replacement:
                values["text"] = "请求内容为空"
            else:
                raise ValueError("文本内容不能为空")

        # 检查文本是否包含至少一个字母或汉字
        if not re.search(r"[a-zA-Z\u4e00-\u9fa5]", text):
            if replacement:
                values["text"] = "请求内容没有文字"
            else:
                raise ValueError("文本内容必须包含至少一个字母或汉字")

        return values
