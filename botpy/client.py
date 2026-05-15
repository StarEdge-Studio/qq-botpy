import asyncio
import traceback
from types import TracebackType
from typing import Any, Callable, Coroutine, Dict, List, Optional, Union, Type

from . import logging
from .api import BotAPI
from .connection import ConnectionSession
from .flags import Intents
from .gateway import BotWebSocket
from .http import BotHttp
from .robot import Robot, Token

_log = logging.get_logger()


class _LoopSentinel:
    __slots__ = ()

    def __getattr__(self, attr: str) -> None:
        raise AttributeError("无法在非异步上下文中访问循环属性")


_loop: Any = _LoopSentinel()


class Client:
    """``Client` 是一个用于与 QQ频道机器人 Websocket 和 API 交互的类。

    使用装饰器注册事件处理函数::

        client = botpy.Client(intents=intents)

        @client.on("at_message_create")
        async def handle_at_message(message: Message):
            await message.reply(content="received")

        client.run(appid="xxx", secret="xxx")
    """

    def __init__(
        self,
        intents: Intents,
        timeout: int = 5,
        is_sandbox=False,
        log_config: Union[str, dict] = None,
        log_format: str = None,
        log_level: int = None,
        bot_log: Union[bool, None] = True,
        ext_handlers: Union[dict, List[dict], bool] = True,
    ):
        """
        Args:
          intents (Intents): 通道：机器人需要注册的通道事件code，通过Intents提供的方法获取。
          timeout (int): 机器人 HTTP 请求的超时时间。. Defaults to 5
          is_sandbox: 是否使用沙盒环境。. Defaults to False

          log_config: 日志配置，可以为dict或.json/.yaml文件路径，会从文件中读取(logging.config.dictConfig)。Default to None（不做更改）
          log_format: 控制台输出格式(logging.basicConfig(format=))。Default to None（不做更改）
          log_level: 控制台输出level。Default to None(不做更改),
          bot_log: bot_log: bot_log: 是否启用bot日志 True/启用 None/禁用拓展 False/禁用拓展+控制台输出
          ext_handlers: ext_handlers: 额外的handler，格式参考 logging.DEFAULT_FILE_HANDLER。Default to True(使用默认追加handler)
        """
        self.intents: int = intents.value
        self.ret_coro: bool = False
        self.loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        self.http: BotHttp = BotHttp(timeout=timeout, is_sandbox=is_sandbox)
        self.api: BotAPI = BotAPI(http=self.http)

        self._connection: Optional[ConnectionSession] = None
        self._closed: bool = False
        self._listeners: Dict[str, List[Tuple[asyncio.Future, Callable[..., bool]]]] = {}
        self._ws_ap: Dict = {}

        self._event_handlers: Dict[str, List[Callable]] = {}

        logging.configure_logging(
            config=log_config,
            _format=log_format,
            level=log_level,
            bot_log=bot_log,
            ext_handlers=ext_handlers,
        )

    def on(self, event: str):
        """装饰器：注册一个WebSocket事件的处理函数。

        用法::

            @client.on("at_message_create")
            async def handle_at_message(message):
                await message.reply(content="hello")

        Args:
          event (str): 事件名称，如 "at_message_create", "c2c_message_create" 等。
        """

        def decorator(func: Callable):
            self.add_listener(func, event)
            return func

        return decorator

    def add_listener(self, func: Callable, event: str = None):
        """添加一个事件监听函数。

        Args:
          func (Callable): 事件处理函数。
          event (str): 事件名称。如果为None，则使用函数名。
        """
        if event is None:
            event = func.__name__
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(func)

    def listen(self, event: str = None):
        """装饰器：注册事件处理函数 (``on`` 的别名)。

        如果未指定事件名称，则使用函数名作为事件名称。

        用法::

            @client.listen()
            async def at_message_create(message):
                await message.reply(content="hello")
        """

        def decorator(func: Callable):
            self.add_listener(func, event)
            return func

        return decorator

    def remove_listener(self, func: Callable, event: str = None):
        """移除已注册的事件监听函数。

        Args:
          func (Callable): 要移除的事件处理函数。
          event (str): 事件名称。如果为None，则使用函数名。
        """
        if event is None:
            event = func.__name__
        if event in self._event_handlers and func in self._event_handlers[event]:
            self._event_handlers[event].remove(func)

    def clear_listeners(self, event: str = None):
        """清除事件监听函数。

        Args:
          event (str): 事件名称。如果为None，则清除所有事件的监听函数。
        """
        if event is None:
            self._event_handlers.clear()
        elif event in self._event_handlers:
            self._event_handlers[event].clear()

    async def __aenter__(self):
        _log.debug("[botpy] 机器人客户端: __aenter__")
        await self._async_setup_hook()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        _log.debug("[botpy] 机器人客户端: __aexit__")

        if not self.is_closed():
            await self.close()

    @property
    def robot(self):
        return self._connection.state.robot

    async def close(self) -> None:
        """关闭client相关的连接"""

        if self._closed:
            return

        self._closed = True

        await self.http.close()

    def is_closed(self) -> bool:
        return self._closed

    async def send_message(self, channel_id: str, content: str = None, **kwargs):
        """主动推送频道消息。

        Args:
          channel_id (str): 子频道 ID。
          content (str): 消息文本内容。
          **kwargs: 其他可选参数，如 embed, ark, markdown, image, file_image, keyboard 等。
        """
        return await self.api.post_message(channel_id=channel_id, content=content, **kwargs)

    async def send_group_message(self, group_openid: str, content: str = None, **kwargs):
        """主动推送群聊消息。

        Args:
          group_openid (str): 群 ID。
          content (str): 消息文本内容。
          **kwargs: 其他可选参数，如 msg_type, embed, ark, markdown, media, keyboard 等。
        """
        return await self.api.post_group_message(group_openid=group_openid, content=content, **kwargs)

    async def send_c2c_message(self, openid: str, content: str = None, **kwargs):
        """主动推送 C2C (私聊) 消息。

        Args:
          openid (str): 用户 ID。
          content (str): 消息文本内容。
          **kwargs: 其他可选参数，如 msg_type, embed, ark, markdown, media, keyboard 等。
        """
        return await self.api.post_c2c_message(openid=openid, content=content, **kwargs)

    async def send_dms_message(self, guild_id: str, content: str = None, **kwargs):
        """主动推送私信消息。

        Args:
          guild_id (str): 私信会话 ID (来自 create_dms 的返回值)。
          content (str): 消息文本内容。
          **kwargs: 其他可选参数，如 embed, ark, markdown, image, file_image, keyboard 等。
        """
        return await self.api.post_dms(guild_id=guild_id, content=content, **kwargs)

    async def on_ready(self):
        pass

    async def on_error(self, event_method: str, *args: Any, **kwargs: Any) -> None:
        traceback.print_exc()

    async def _async_setup_hook(self) -> None:
        # Called whenever the client needs to initialise asyncio objects with a running loop
        self.loop = asyncio.get_running_loop()
        self._ready = asyncio.Event()

    def run(self, *args: Any, **kwargs: Any) -> None:
        """
        机器人服务开始执行

        注意:
          这个函数必须是最后一个调用的函数，因为它是阻塞的。这意味着事件的注册或在此函数调用之后调用的任何内容在它返回之前不会执行。
          如果想获取协程对象，可以使用`start`方法执行服务, 如:
        ```
        async with Client as c:
            c.start()
        ```
        """

        async def runner():
            async with self:
                await self.start(*args, **kwargs)

        try:
            self.loop.run_until_complete(runner())
        except KeyboardInterrupt:
            return

    async def start(self, appid: str, secret: str, ret_coro: bool = False) -> Optional[Coroutine]:
        """机器人开始执行

        参数
        ------------
        appid: :class:`str`
            机器人 appid
        secret: :class:`str`
            机器人 secret
        ret_coro: :class:`bool`
            是否需要返回协程对象
        """
        # login后再进行后面的操作
        token = Token(appid, secret)
        self.ret_coro = ret_coro

        if self.loop is _loop:
            await self._async_setup_hook()

        await self._bot_login(token)
        return await self._bot_init(token)

    async def _bot_login(self, token: Token) -> None:
        _log.info("[botpy] 登录机器人账号中...")

        user = await self.http.login(token)

        # 通过api获取websocket链接
        self._ws_ap = await self.api.get_ws_url()

        # 实例一个session_pool
        self._connection = ConnectionSession(
            max_async=self._ws_ap["session_start_limit"]["max_concurrency"],
            connect=self.bot_connect,
            dispatch=self.ws_dispatch,
            loop=self.loop,
            api=self.api,
        )

        self._connection.state.robot = Robot(user)

    async def _bot_init(self, token):
        _log.info("[botpy] 程序启动...")
        # 每个机器人创建的连接数不能超过remaining剩余连接数
        if self._ws_ap["shards"] > self._ws_ap["session_start_limit"]["remaining"]:
            raise Exception("[botpy] 超出会话限制...")

        # 根据session限制建立链接
        concurrency = self._ws_ap["session_start_limit"]["max_concurrency"]
        session_interval = round(5 / concurrency)

        # 根据限制建立分片的并发链接数
        _log.debug(f'[botpy] 会话间隔: {session_interval}, 分片: {self._ws_ap["shards"]}, 事件代码: {self.intents}')
        return await self._pool_init(token.bot_token(), session_interval)

    async def _pool_init(self, token, session_interval):
        def _loop_exception_handler(_loop, context):
            # first, handle with default handler
            _loop.default_exception_handler(context)

            exception = context.get("exception")
            if isinstance(exception, ZeroDivisionError):
                _loop.stop()

        for i in range(self._ws_ap["shards"]):
            session = {
                "session_id": "",
                "last_seq": 0,
                "intent": self.intents,
                "token": token,
                "url": self._ws_ap["url"],
                "shards": {"shard_id": i, "shard_count": self._ws_ap["shards"]},
            }
            self._connection.add(session)

        loop = self._connection.loop
        loop.set_exception_handler(_loop_exception_handler)

        while not self._closed:
            _log.debug("[botpy] 会话循环检查...")
            try:
                # 返回协程对象，交由开发者自行调控
                coroutine = self._connection.multi_run(session_interval)
                if self.ret_coro:
                    return coroutine
                elif coroutine:
                    await coroutine
                else:
                    await self.close()
                    _log.info("[botpy] 服务意外停止!")
            except KeyboardInterrupt:
                _log.info("[botpy] 服务强行停止!")
                # cancel all tasks lingering

    async def bot_connect(self, session):
        """
        newConnect 启动一个新的连接，如果连接在监听过程中报错了，或者被远端关闭了链接，需要识别关闭的原因，能否继续 resume
        如果能够 resume，则往 sessionChan 中放入带有 sessionID 的 session
        如果不能，则清理掉 sessionID，将 session 放入 sessionChan 中
        session 的启动，交给 start 中的 for 循环执行，session 不自己递归进行重连，避免递归深度过深

        param session: session对象
        """
        _log.info("[botpy] 会话启动中...")

        client = BotWebSocket(session, self._connection)
        try:
            await client.ws_connect()
        except (Exception, KeyboardInterrupt, SystemExit) as e:
            await client.on_error(e)

    def ws_dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        """分发ws的下行事件

        优先通过装饰器注册的监听函数处理，同时兼容旧的 on_EVENT 命名约定。
        """
        _log.debug("[botpy] 调度事件: %s", event)
        dispatched = False

        # 新的装饰器注册方式：通过 @client.on("event_name") 注册
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                self._schedule_event(handler, event, *args, **kwargs)
                dispatched = True

        # 旧的命名约定方式：on_eventname (向后兼容)
        method = "on_" + event
        if hasattr(self, method):
            coro = getattr(self, method)
            self._schedule_event(coro, method, *args, **kwargs)
            dispatched = True

        if not dispatched:
            _log.debug("[botpy] 事件: %s 未注册", event)

    def _schedule_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> asyncio.Task:
        wrapped = self._run_event(coro, event_name, *args, **kwargs)
        # Schedules the task
        return self.loop.create_task(wrapped, name=f"[botpy] {event_name}")

    async def _run_event(
        self,
        coro: Callable[..., Coroutine[Any, Any, Any]],
        event_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        try:
            _log.debug("[botpy] _run_event")
            await coro(*args, **kwargs)
        except asyncio.CancelledError:
            pass
        except Exception:
            try:
                await self.on_error(event_name, *args, **kwargs)
            except asyncio.CancelledError:
                pass
