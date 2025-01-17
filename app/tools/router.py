# -*- coding: utf-8 -*-
"""
路由定义
"""

import json
import base64
from os import getenv
import edge_tts
from fastapi import Request
from fastapi.responses import PlainTextResponse, JSONResponse
from fastflyer.schemas import DataResponse
from fastapi.exceptions import HTTPException
from fastapi import Query
from fastflyer import APIRouter, status, config
from fastkit.cache import get_cacheout_pool
from .schema import TTSToolsRequest

router = APIRouter(tags=["实用工具"], prefix="/tools")

local_cache = get_cacheout_pool("tts")


async def get_origin_url(request: Request) -> str:
    """获取原始url"""
    scheme = request.headers.get("X-Forwarded-Proto") or request.url.scheme
    host = request.headers.get("X-Forwarded-Host") or request.headers.get("Host") or request.url.hostname
    return f"{scheme}://{host}"


async def get_headers(request: Request) -> dict:
    """获取请求头部"""
    flyer_auth_enable = int(getenv("flyer_auth_enable") or "0")
    if not flyer_auth_enable:
        return {}
    username = getenv("flyer_auth_user", "")
    password = getenv("flyer_auth_pass", "")
    client_auth_user = request.query_params.get("username", "")
    client_auth_pass = request.query_params.get("password", "")
    if client_auth_user != username or client_auth_pass != password:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "认证失败，请在url参数中填写正确的用户名（username）和密码参数（password）"
        )
    encoded_credentials = base64.b64encode(f"{username}:{password}".encode("utf-8")).decode("utf-8")
    return {"headers": {"Authorization": f"Basic {encoded_credentials}", "Content-Type": "application/json"}}


@router.get("/voices", response_model=DataResponse, summary="实时获取所有语音列表")
async def get_voices(
    keyword: str = Query(default="", example="", title="过滤关键词", description="过滤关键词"),
    format: str = Query(
        default="short",
        example="short",
        title="返回内容",
        description="返回内容，可选 full / short，默认为 short 即简洁列表",
    ),
):
    @local_cache.cache_result(ttl=86400)
    async def _get_all_voices():
        """获取所有语音列表"""
        return await edge_tts.list_voices()

    async def _get_voices(keyword: str = None, format: str = "short"):
        """根据关键词获取语音列表"""
        data = await _get_all_voices()
        if keyword:
            data = [voice for voice in data if str(keyword).lower() in voice["ShortName"].lower()]

        if format == "short":
            data = [voice["ShortName"] for voice in data]

        return data

    try:
        voices = await _get_voices(keyword, format)
        return DataResponse(data=voices)
    except Exception as e:
        return DataResponse(code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=f"获取错误：{str(e)}")


@router.get("/legado/url", summary="一键生成源阅读url")
async def legado_url(request: Request, params: TTSToolsRequest = Query()):
    """
    一键生成源阅读url
    """
    origin = await get_origin_url(request)
    payload = {
        "method": "POST",
        "body": {
            "text": "{{speakText}}",
            "voice": params.voice,
            "volume": params.volume,
            "rate": "{{String(speakSpeed)}}%",
            "pitch": params.pitch,
        },
    }
    headers = await get_headers(request)
    payload.update(headers)

    payload = json.dumps(payload)
    url = f"{origin}{config.PREFIX}/stream, {payload}"
    return PlainTextResponse(content=url)


@router.get("/legado/import", summary="一键导入源阅读语音配置")
async def legado_import(request: Request, params: TTSToolsRequest = Query()):
    """
    一键导入源阅读语音配置
    """
    origin = await get_origin_url(request)
    payload = {
        "method": "POST",
        "body": {
            "text": "{{speakText}}",
            "voice": params.voice,
            "volume": params.volume,
            "rate": "{{String(speakSpeed)}}%",
            "pitch": params.pitch,
        },
    }

    headers = await get_headers(request)
    payload.update(headers)

    payload = json.dumps(payload)
    url = f"{origin}{config.PREFIX}/stream, {payload}"
    content = {
        "contentType": "audio/mp3",
        "enabledCookieJar": False,
        "name": "FastTTS",
        "url": url,
    }
    return JSONResponse(content=content)
