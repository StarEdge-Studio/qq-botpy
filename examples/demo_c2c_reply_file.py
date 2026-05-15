# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.ext.cog_yaml import read
from botpy.message import C2CMessage

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(public_messages=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("c2c_message_create")
async def handle_c2c_message(message: C2CMessage):
    file_url = ""  # 这里需要填写上传的资源Url
    uploadMedia = await message.api.post_c2c_file(
        openid=message.author.user_openid,
        file_type=1,  # 文件类型要对应上，具体支持的类型见方法说明
        url=file_url  # 文件Url
    )

    # 资源上传后，会得到Media，用于发送消息
    await message.api.post_c2c_message(
        openid=message.author.user_openid,
        msg_type=7,  # 7表示富媒体类型
        msg_id=message.id,
        media=uploadMedia
    )


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
