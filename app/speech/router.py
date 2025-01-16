# -*- coding: utf-8 -*-
"""
路由定义
"""
import random
from io import BytesIO
from asyncio import sleep
import edge_tts
from fastapi import Request
from fastapi.responses import StreamingResponse
from fastflyer.schemas import DataResponse
from fastflyer import APIRouter, logger
from fastkit.cache import get_cacheout_pool
from .schema import TTSFullRequest


router = APIRouter(tags=["语音合成"])

local_cache = get_cacheout_pool("tts")


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
    audio_stream = stream_audio(
        text=params.text, voice=params.voice, rate=params.rate, volume=params.volume, pitch=params.pitch
    )
    return StreamingResponse(audio_stream, media_type="audio/mp3")


@router.post("/file", response_model=DataResponse, summary="语音合成音频文件接口")
async def make_file(params: TTSFullRequest):
    """
    语音合成音频文件接口
    """
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
