# -*- coding: utf-8 -*-
import botpy
from botpy import logging
from botpy.forum import OpenThread

_log = logging.get_logger()

client = botpy.Client(intents=botpy.Intents(open_forum_event=True))


@client.on("ready")
async def handle_ready():
    _log.info(f"robot 「{client.robot.name}」 on_ready!")


@client.on("open_forum_thread_create")
async def handle_thread_create(open_forum_thread: OpenThread):
    _log.info("%s 创建了主题" % open_forum_thread.author_id)


@client.on("open_forum_thread_update")
async def handle_thread_update(open_forum_thread: OpenThread):
    _log.info("%s 更新了主题" % open_forum_thread.author_id)


@client.on("open_forum_thread_delete")
async def handle_thread_delete(open_forum_thread: OpenThread):
    _log.info("%s 删除了主题" % open_forum_thread.author_id)


@client.on("open_forum_post_create")
async def handle_post_create(open_forum_thread: OpenThread):
    _log.info("%s 创建了帖子" % open_forum_thread.author_id)


@client.on("open_forum_post_delete")
async def handle_post_delete(open_forum_thread: OpenThread):
    _log.info("%s 删除了帖子" % open_forum_thread.author_id)


@client.on("open_forum_reply_create")
async def handle_reply_create(open_forum_thread: OpenThread):
    _log.info("%s 发表了评论" % open_forum_thread.author_id)


@client.on("open_forum_reply_delete")
async def handle_reply_delete(open_forum_thread: OpenThread):
    _log.info("%s 删除了评论" % open_forum_thread.author_id)


if __name__ == "__main__":
    client.run(appid="appid", secret="secret")
