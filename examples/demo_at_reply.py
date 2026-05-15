# -*- coding: utf-8 -*-
import asyncio
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import Message

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_guild_messages=True))


@client.on("at_message_create")
async def handle_at_message(message: Message):
    _log.info(message.author.avatar)
    if "sleep" in message.content:
        await asyncio.sleep(10)
    _log.info(message.author.username)
    await message.reply(content=f"机器人{client.robot.name}收到你的@消息了: {message.content}")


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
