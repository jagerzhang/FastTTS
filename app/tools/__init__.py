# -*- coding: utf-8 -*-
"""
包入口
"""
# 导入路由对象（导入后的对象必须为 router 才能被识别）
from .router import router  # noqa

# 工具接口不鉴权
__AUTH_ENABLED__ = False
