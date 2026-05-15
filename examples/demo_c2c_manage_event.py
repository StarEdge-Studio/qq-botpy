# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.manage import C2CManageEvent

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_messages=True))


@client.on("friend_add")
async def handle_friend_add(event: C2CManageEvent):
    _log.info("用户添加机器人：" + str(event))
    await client.api.post_c2c_message(
        openid=event.openid,
        msg_type=0,
        event_id=event.event_id,
        content="hello",
    )


@client.on("friend_del")
async def handle_friend_del(event: C2CManageEvent):
    _log.info("用户删除机器人：" + str(event))


@client.on("c2c_msg_reject")
async def handle_c2c_msg_reject(event: C2CManageEvent):
    _log.info("用户关闭机器人主动消息：" + str(event))


@client.on("c2c_msg_receive")
async def handle_c2c_msg_receive(event: C2CManageEvent):
    _log.info("用户打开机器人主动消息：" + str(event))


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
