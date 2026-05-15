# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import GroupMessage
from botpy.types.message import MarkdownPayload

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("group_message_create")
async def handle_group_message(message: GroupMessage):
    _log.info(f"收到群消息: {message.content}, 发送者: {message.author.member_openid}")

    # @ 发送者（自动转为 markdown，因为 @ 标签仅 markdown 支持）
    await message.reply(at_user=True, content="收到了你的消息")

    # @ 发送者 + 按钮
    await message.reply(at_user=True, markdown=MarkdownPayload(content="请选择"), keyboard={"id": "62"})

    # 仅发送 markdown + 按钮
    await message.reply(markdown=MarkdownPayload(content="# 标题"), keyboard={"id": "62"})

    # 普通文本回复
    await message.reply(content="收到消息")


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
