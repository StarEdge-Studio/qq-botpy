# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.user import Member
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(guild_members=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("guild_member_add")
async def handle_guild_member_add(member: Member):
    _log.info("%s 加入频道" % member.nick)
    dms_payload = await client.api.create_dms(member.guild_id, member.user.id)
    _log.info("发送私信")
    await client.api.post_dms(dms_payload["guild_id"], content="welcome join guild", msg_id=member.event_id)


@client.on("guild_member_update")
async def handle_guild_member_update(member: Member):
    _log.info("%s 更新了资料" % member.nick)


@client.on("guild_member_remove")
async def handle_guild_member_remove(member: Member):
    _log.info("%s 退出了频道" % member.nick)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
