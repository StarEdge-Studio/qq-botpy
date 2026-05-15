# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging, BotAPI
from botpy.ext.command_util import Commands
from botpy.message import Message
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_guild_messages=True))


@Commands("你好", "hello")
async def hello(api: BotAPI, message: Message, params=None):
    _log.info(params)
    await message.reply(content=params)
    return True


@Commands("晚安")
async def good_night(api: BotAPI, message: Message, params=None):
    _log.info(params)
    await message.reply(content=params)
    return True


@client.on("at_message_create")
async def handle_at_message(message: Message):
    handlers = [hello, good_night]
    for handler in handlers:
        if await handler(api=client.api, message=message):
            return


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
