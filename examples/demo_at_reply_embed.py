# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.message import Message
from botpy.types.message import Embed, EmbedField
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_guild_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("at_message_create")
async def handle_at_message(message: Message):
    embed = Embed(
        title="embed消息",
        prompt="消息透传显示",
        fields=[
            EmbedField(name="<@!1234>hello world"),
            EmbedField(name="<@!1234>hello world"),
        ],
    )
    await message.reply(embed=embed)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
