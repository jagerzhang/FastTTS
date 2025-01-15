# -*- coding: utf-8 -*-
"""
路由定义
"""
from io import BytesIO
import edge_tts
from fastapi import Request
from fastapi.responses import StreamingResponse
from fastflyer.schemas import DataResponse
from fastflyer import APIRouter
from fastkit.cache import get_cacheout_pool
from .schema import TTSFullRequest


router = APIRouter(tags=["语音合成"])

local_cache = get_cacheout_pool("tts")


async def get_origin_url(request: Request) -> str:
    """获取原始url"""
    scheme = request.headers.get("X-Forwarded-Proto") or request.url.scheme
    host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host") or request.url.hostname
    return f"{scheme}://{host}"


async def stream_audio(text, voice, rate, volume, pitch) -> None:
    """生成音频流"""
    communicate = edge_tts.Communicate(text=text, voice=voice, rate=rate, volume=volume, pitch=pitch)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


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
