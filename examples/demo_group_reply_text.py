# -*- coding: utf-8 -*-
import asyncio
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("group_at_message_create")
async def handle_group_at_message(message: GroupMessage):
    result = await message.reply(
        msg_type=0,
        content=f"收到了消息：{message.content}"
    )
    _log.info(result)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
