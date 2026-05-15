# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.types.message import Reference
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
    # 方式1：reply(quote=True) 自动生成引用
    await message.reply(content="<emoji:4>这是一条引用消息", quote=True)

    # 方式2：手动传入 message_reference
    message_reference = Reference(message_id=message.id)
    await message.reply(
        content="<emoji:4>这也是一条引用消息",
        message_reference=message_reference,
    )


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
