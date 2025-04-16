# -*- coding: utf-8 -*-
"""
路由定义
"""
import re
import random
from io import BytesIO
from asyncio import sleep
import edge_tts
from fastapi import Request
from fastapi.responses import StreamingResponse
from fastflyer.schemas import DataResponse
from fastflyer import APIRouter, logger
from fastkit.cache import get_cacheout_pool
from pydub import AudioSegment

from .schema import TTSFullRequest


router = APIRouter(tags=["语音合成"])

local_cache = get_cacheout_pool("tts")


def check_text(text):
    """检测文本内容是否有文字"""
    if not re.search(r"[a-zA-Z\u4e00-\u9fa5]", text):
        return False
    return True


def generated_empty_audio(duration: int = 1000):
    """生成空白音频文件"""
    silence = AudioSegment.silent(duration=duration)
    return BytesIO(silence.export(format="mp3").read())


async def get_origin_url(request: Request) -> str:
    """获取原始url"""
    scheme = request.headers.get("X-Forwarded-Proto") or request.url.scheme
    host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host") or request.url.hostname
    return f"{scheme}://{host}"


async def generate_audio_stream(text, voice, rate, volume, pitch, retries=10):
    """生成音频流并处理重试逻辑"""
    for attempt in range(retries):
        try:
            communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume, pitch=pitch)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]
            break  # 如果成功，跳出循环
        except Exception as e:
            logger.warning(f"音频流获取失败: {e}，尝试重新获取，第 {attempt + 1} 次重试")
            if attempt == retries - 1:
                raise e
            await sleep(random.randint(1, 3))


async def stream_audio(text, voice, rate, volume, pitch):
    """包装生成音频流的函数"""
    async for audio_chunk in generate_audio_stream(text, voice, rate, volume, pitch):
        yield audio_chunk


@router.post("/stream", response_model=DataResponse, summary="语音合成音频流接口")
async def stream(params: TTSFullRequest):
    """
    语音合成音频流接口
    """
    # 当传入内容没有文字时，返回1秒空白音频，避免源阅读报错终止
    if not check_text(params.text):
        audio_stream = generated_empty_audio()
        return StreamingResponse(audio_stream, media_type="audio/mp3")

    audio_stream = stream_audio(
        text=params.text, voice=params.voice, rate=params.rate, volume=params.volume, pitch=params.pitch
    )
    return StreamingResponse(audio_stream, media_type="audio/mp3")


@router.post("/file", response_model=DataResponse, summary="语音合成音频文件接口")
async def make_file(params: TTSFullRequest):
    """
    语音合成音频文件接口
    """
    # 当传入内容没有文字时，返回1秒空白音频，避免源阅读报错终止
    if not check_text(params.text):
        audio_stream = generated_empty_audio()
        return StreamingResponse(audio_stream, media_type="audio/mp3",
                                 headers={"Content-Disposition": "attachment; filename=output.mp3"})

    audio_buffer = BytesIO()
    async for chunk in stream_audio(
        text=params.text, voice=params.voice, rate=params.rate, volume=params.volume, pitch=params.pitch
    ):
        audio_buffer.write(chunk)

    audio_buffer.seek(0)
    return StreamingResponse(
        audio_buffer,
        media_type="audio/mp3",
        headers={"Content-Disposition": "attachment; filename=output.mp3"},
    )
