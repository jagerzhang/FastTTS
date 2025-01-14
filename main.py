# -*- coding: utf-8 -*-
from os import getenv, path
import uvicorn
from fastflyer import FlyerAPI

root_path = path.dirname(path.abspath(__file__))
app_path = f"{root_path}/app"
app = FlyerAPI(app_path=app_path)


def main():
    """
    通过shell执行uvicorn启动
    """
    pass


def main_cmd():
    """
    直接执行 main.py 启动
    """
    bind_host = getenv("flyer_host", "0.0.0.0")
    bind_port = getenv("flyer_port", 8080)
    workers = int(getenv("flyer_workers", 1))
    reload = int(getenv("flyer_reload", 0))
    log_level = getenv("flyer_console_log_level", "info")
    access_log = True if int(getenv("flyer_access_log", "1")) else False
    uvicorn.run(app="main:app",
                host=bind_host,
                port=int(bind_port),
                log_level=log_level,
                access_log=access_log,
                reload=reload,
                workers=workers)


if __name__ == "__main__":
    main_cmd()
