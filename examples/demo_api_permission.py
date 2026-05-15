# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.message import Message
from botpy.types.permission import APIPermissionDemandIdentify
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_guild_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("at_message_create")
async def handle_at_message(message: Message):
    # 先发送消息告知用户
    await message.reply(content=f"机器人{client.robot.name}创建日程{message.content}")

    # 输入/xxx后的处理
    if "/权限列表" in message.content:
        apis = await client.api.get_permissions(message.guild_id)
        for api in apis:
            _log.info("api: %s" % api["desc"] + ", status: %d" % api["auth_status"])
    if "/请求权限" in message.content:
        demand_identity = APIPermissionDemandIdentify(path="/guilds/{guild_id}/members/{user_id}", method="GET")
        demand = await client.api.post_permission_demand(
            message.guild_id, message.channel_id, demand_identity, "获取当前频道成员信息"
        )
        _log.info("api title: %s" % demand["title"] + ", desc: %s" % demand["desc"])


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
