# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.message import Message
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_guild_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("at_message_create")
async def handle_at_message(message: Message):
    _message = await message.reply(content=f"机器人{client.robot.name}收到你的@消息了: {message.content}")
    await client.api.recall_message(message.channel_id, _message.get("id"), hidetip=True)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
