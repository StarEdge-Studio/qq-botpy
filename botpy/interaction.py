from .api import BotAPI
from .types import interaction


class Interaction:
    __slots__ = (
        "api",
        "id",
        "application_id",
        "type",
        "scene",
        "chat_type",
        "event_id",
        "data",
        "guild_id",
        "channel_id",
        "user_openid",
        "group_openid",
        "group_member_openid",
        "timestamp",
        "version",
    )

    def __init__(self, api: BotAPI, event_id, data: interaction.InteractionPayload):
        self.api = api

        self.id = data.get("id", None)
        self.type = data.get("type", None)
        self.scene = data.get("scene", None)
        self.chat_type = data.get("chat_type", None)
        self.application_id = data.get("application_id", None)
        self.event_id = event_id
        self.data = self._Data(data.get("data", {}))
        self.guild_id = data.get("guild_id", None)
        self.channel_id = data.get("channel_id", None)
        self.user_openid = data.get("user_openid", None)
        self.group_openid = data.get("group_openid", None)
        self.group_member_openid = data.get("group_member_openid", None)
        self.timestamp = data.get("timestamp", None)
        self.version = data.get("version", None)

    def __repr__(self):
        return str({items: str(getattr(self, items)) for items in self.__slots__ if not items.startswith("_")})

    class _Data:
        def __init__(self, data):
            self.type = data.get("type", None)
            self.resolved = Interaction._Resolved(data.get("resolved", None))

        def __repr__(self):
            return str(self.__dict__)

    class _Resolved:
        def __init__(self, data):
            self.button_id = data.get("button_id", None)
            self.button_data = data.get("button_data", None)
            self.message_id = data.get("message_id", None)
            self.user_id = data.get("user_id", None)
            self.feature_id = data.get("feature_id", None)

        def __repr__(self):
            return str(self.__dict__)

    async def reply(self, content: str = None, **kwargs):
        """回复按钮点击事件。

        根据 chat_type / scene 自动选择正确的发送方式，并使用交互事件的 event_id 进行回复：
        - 频道消息 (chat_type=0): 发送到对应频道子频道
        - 群聊消息 (chat_type=1): 发送到对应群
        - C2C消息 (chat_type=2): 发送到对应用户

        Args:
          content (str): 消息文本内容。
          **kwargs: 其他可选参数。
        """
        if self.chat_type == 0:
            return await self.api.post_message(
                channel_id=self.channel_id,
                content=content,
                event_id=self.id,
                **kwargs,
            )
        elif self.chat_type == 1:
            return await self.api.post_group_message(
                group_openid=self.group_openid,
                content=content,
                event_id=self.id,
                **kwargs,
            )
        elif self.chat_type == 2:
            return await self.api.post_c2c_message(
                openid=self.user_openid,
                content=content,
                event_id=self.id,
                **kwargs,
            )
