# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.message import DirectMessage, Message
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(direct_message=True, public_guild_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("direct_message_create")
async def handle_direct_message(message: DirectMessage):
    await message.reply(
        content=f"机器人{client.robot.name}收到你的私信了: {message.content}"
    )


@client.on("at_message_create")
async def handle_at_message(message: Message):
    if "/私信" in message.content:
        dms_payload = await client.api.create_dms(message.guild_id, message.author.id)
        _log.info("发送私信")
        await client.api.post_dms(dms_payload["guild_id"], content="hello", msg_id=message.id)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
