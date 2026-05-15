# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.message import Message
from botpy.types.message import MarkdownPayload, MessageMarkdownParams
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_guild_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


async def send_markdown_by_template(message: Message):
    params = [
        MessageMarkdownParams(key="title", values=["标题"]),
        MessageMarkdownParams(key="content", values=["为了成为一名合格的巫师，请务必阅读频道公告", "藏馆黑色魔法书"]),
    ]
    markdown = MarkdownPayload(custom_template_id="65", params=params)
    await message.reply(markdown=markdown)


async def send_markdown_by_content(message: Message):
    markdown = MarkdownPayload(content="# 标题 \n## 简介很开心 \n内容")
    await message.reply(markdown=markdown)


@client.on("at_message_create")
async def handle_at_message(message: Message):
    await message.reply(content=f"机器人{client.robot.name}收到你的@消息了: {message.content}")
    await send_markdown_by_template(message)
    await send_markdown_by_content(message)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
