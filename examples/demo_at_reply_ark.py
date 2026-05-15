# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.message import Message
from botpy.types.message import Ark, ArkKv
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_guild_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("at_message_create")
async def handle_at_message(message: Message):
    payload: Ark = Ark(
        template_id=37,
        kv=[
            ArkKv(key="#METATITLE#", value="通知提醒"),
            ArkKv(key="#PROMPT#", value="标题"),
            ArkKv(key="#TITLE#", value="标题"),
            ArkKv(key="#METACOVER#", value="https://vfiles.gtimg.cn/vupload/20211029/bf0ed01635493790634.jpg"),
        ],
    )
    await message.reply(ark=payload)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
