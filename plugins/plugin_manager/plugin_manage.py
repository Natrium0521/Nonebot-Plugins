from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.plugin import on_startswith
from nonebot.rule import to_me
import json
import nonebot
import os
import re

from .plugin_state import checkAllow, getPlugins, setPlugins

manager = on_startswith(msg={"开启", "关闭"}, rule=to_me(), priority=1, block=True)


@manager.handle()
async def _(event: Event):
    if event.get_user_id() in nonebot.get_driver().config.other_bots:
        return
    cmd = str(event.get_message())[:2]
    msg = str(event.get_message())[2:]
    msg = re.sub(" ", "", msg)
    isGroupMessage: bool
    if event.get_event_name() == "message.group.normal":
        isGroupMessage = True
    elif event.get_event_name() == "message.private.friend":
        isGroupMessage = False
    else:
        return
    _id = str(event.group_id if isGroupMessage else event.user_id)
    plugins = getPlugins()
    if msg == "":
        await manager.finish("缺少插件名称, 使用帮助查看启用插件")
    else:
        message = msg
        if msg not in plugins:
            message += "不在插件列表"
        else:
            if checkAllow(isGroupMessage, msg, _id):
                on = "on_group" if isGroupMessage else "on_user"
                off = "off_group" if isGroupMessage else "off_user"
                if cmd == "关闭":
                    on, off = off, on
                if ("all" in plugins[msg][on]) and (_id in plugins[msg][off]):
                    plugins[msg][off].remove(_id)
                elif ("all" in plugins[msg][off]) and (_id not in plugins[msg][on]):
                    plugins[msg][on].append(_id)
                setPlugins(plugins)
                message += f"已{cmd}"
            else:
                message += "未启用"
        await manager.finish(Message(message))
