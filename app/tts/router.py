# -*- coding: utf-8 -*-
"""
路由定义
"""

import json
from io import BytesIO
import edge_tts
from fastapi import Request
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastflyer.schemas import DataResponse
from fastflyer import APIRouter, status
from .schema import TTSBaseRequest, TTSFullRequest


router = APIRouter(tags=["语音合成"])


async def stream_audio(text, voice, **kwargs) -> None:
    """生成音频流"""
    communicate = edge_tts.Communicate(text, voice)
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]


@router.post("/stream", response_model=DataResponse, summary="语音合成音频流接口")
async def stream(params: TTSFullRequest):
    """
    语音合成音频流接口
    """
    audio_stream = stream_audio(text=params.text, voice=params.voice)
    return StreamingResponse(audio_stream, media_type="application/octet-stream")


@router.post("/file", response_model=DataResponse, summary="语音合成音频文件接口")
async def make_file(params: TTSFullRequest):
    """
    语音合成音频文件接口
    """
    audio_buffer = BytesIO()
    async for chunk in stream_audio(text=params.text, voice=params.voice):
        audio_buffer.write(chunk)

    audio_buffer.seek(0)
    return StreamingResponse(
        audio_buffer,
        media_type="application/octet-stream",
        headers={"Content-Disposition": "attachment; filename=output.mp3"},
    )


@router.get("/voices", response_model=DataResponse, summary="获取所有语音列表")
async def get_voices():
    try:
        voices = await edge_tts.list_voices()
        return DataResponse(data=voices)
    except Exception as e:
        return DataResponse(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=f"获取错误：{str(e)}")


@router.post("/legado_url", summary="一键生成源阅读url")
async def legado(request: Request, params: TTSBaseRequest):
    """
    一键生成源阅读url
    """
    origin = request.headers.get("origin", "http://localhost:8080")
    payload = {
        "method": "POST",
        "body": {
            "text": "{{speakText}}",
            "voice": params.voice,
            "volume": params.volume,
            "rate": "{{String(speakSpeed)}}",
            "pitch": params.pitch,
        },
    }
    payload = json.dumps(payload)
    url = f"{origin}/tts/stream, {payload}"
    return PlainTextResponse(content=url)
