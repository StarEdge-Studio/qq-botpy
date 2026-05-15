# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.manage import GroupManageEvent

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_messages=True))


@client.on("group_add_robot")
async def handle_group_add_robot(event: GroupManageEvent):
    _log.info("机器人被添加到群聊：" + str(event))
    await client.api.post_group_message(
        group_openid=event.group_openid,
        msg_type=0,
        event_id=event.event_id,
        content="hello",
    )


@client.on("group_del_robot")
async def handle_group_del_robot(event: GroupManageEvent):
    _log.info("机器人被移除群聊：" + str(event))


@client.on("group_msg_reject")
async def handle_group_msg_reject(event: GroupManageEvent):
    _log.info("群聊关闭机器人主动消息：" + str(event))


@client.on("group_msg_receive")
async def handle_group_msg_receive(event: GroupManageEvent):
    _log.info("群聊打开机器人主动消息：" + str(event))


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
