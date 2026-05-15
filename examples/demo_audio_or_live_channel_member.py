# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.audio import PublicAudio
from botpy.ext.cog_yaml import read

_log = logging.get_logger()

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

client = botpy.Client(intents=botpy.Intents(audio_or_live_channel_member=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("audio_or_live_channel_member_enter")
async def handle_member_enter(public_audio: PublicAudio):
    if public_audio.channel_type == 2:
        _log.info("%s 加入了音视频子频道" % public_audio.user_id)
    elif public_audio.channel_type == 5:
        _log.info("%s 加入了直播子频道" % public_audio.user_id)


@client.on("audio_or_live_channel_member_exit")
async def handle_member_exit(public_audio: PublicAudio):
    if public_audio.channel_type == 2:
        _log.info("%s 退出了音视频子频道" % public_audio.user_id)
    elif public_audio.channel_type == 5:
        _log.info("%s 退出了直播子频道" % public_audio.user_id)


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
