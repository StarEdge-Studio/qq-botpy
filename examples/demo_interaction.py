# -*- coding: utf-8 -*-
import os

import botpy
from botpy import logging
from botpy.interaction import Interaction
from botpy.ext.cog_yaml import read

test_config = read(os.path.join(os.path.dirname(__file__), "config.yaml"))

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(interaction=True, public_messages=True))


@client.on("interaction_create")
async def handle_interaction(interaction: Interaction):
    # 谁点击了按钮
    who = interaction.user_openid or interaction.data.resolved.user_id
    # 哪个按钮
    button = interaction.data.resolved.button_id
    # 按钮携带的数据
    btn_data = interaction.data.resolved.button_data

    _log.info(f"用户 {who} 点击了按钮 {button}, 数据: {btn_data}")

    if btn_data == "/搜索":
        # reply 内部使用 interaction.id 作为 event_id，实现互动回复
        await interaction.reply(content=f"搜索结果...")
    elif btn_data == "/确认":
        await interaction.reply(content="操作已确认")


if __name__ == "__main__":
    client.run(appid=test_config["appid"], secret=test_config["secret"])
