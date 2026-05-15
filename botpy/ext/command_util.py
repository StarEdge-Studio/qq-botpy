# -*- coding: utf-8 -*-
from functools import wraps
from botpy.message import Message, BaseMessage


class Commands:
    """
    指令装饰器

    用法::

        @Commands("你好", "hello")
        async def hello(api, message, params=None):
            await message.reply(content=params)
            return True

    Args:
      args (tuple): 字符串元组，匹配指令关键词。
    """

    def __init__(self, *args):
        self.commands = args

    def __call__(self, func):
        @wraps(func)
        async def decorated(*args, **kwargs):
            message: BaseMessage = kwargs.get("message")
            if message is None:
                return False
            for command in self.commands:
                if command in message.content:
                    params = message.content.split(command)[1].strip()
                    kwargs["params"] = params
                    return await func(*args, **kwargs)
            return False

        return decorated
