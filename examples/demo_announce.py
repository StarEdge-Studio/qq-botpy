# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.message import Message
from botpy.types.announce import AnnouncesType
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_guild_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("at_message_create")
async def handle_at_message(message: Message):
    _log.info(f"{client.robot.name}receive message {message.content}")

    # 先发送消息告知用户
    await client.send_message(message.channel_id, content="command received: %s" % message.content)

    # 输入/xxx后的处理
    # 对用户引用回复的消息设置/删除公告
    message_id = message.message_reference.message_id
    if "/建公告" in message.content:
        await client.api.create_announce(message.guild_id, message.channel_id, message_id)

    elif "/删公告" in message.content:
        await client.api.delete_announce(message.guild_id, message_id)

    elif "/设置推荐子频道" in message.content:
        channel_list = [{"channel_id": message.channel_id, "introduce": "introduce"}]
        await client.api.create_recommend_announce(message.guild_id, AnnouncesType.MEMBER, channel_list)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
