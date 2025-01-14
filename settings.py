from fastflyer.settings import BaseConfig


class CustomConfig(BaseConfig):
    """
    自定义配置

    Args:
        BaseConfig (_type_): 框架默认配置
    """
    # 修改项目标题
    API_TITLE = "Flyer Demo"
    # 其他变量请参考BaseConfig内容
