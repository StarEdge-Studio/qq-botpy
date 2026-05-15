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
    await message.reply(content=f"机器人{client.robot.name}收到你的@消息了: {message.content}")
    if "/获取精华列表" in message.content:
        pins_message = await client.api.get_pins(message.channel_id)
        _log.info(pins_message)

    if "/创建精华消息" in message.content:
        pins_message = await client.api.put_pin(message.channel_id, message.id)
        _log.info(pins_message)

    if "/删除精华消息" in message.content:
        result = await client.api.delete_pin(message.channel_id, message.id)
        _log.info(result)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
