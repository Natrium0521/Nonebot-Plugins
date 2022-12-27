from nonebot.adapters.onebot.v11 import Event, GroupMessageEvent
from nonebot.adapters.onebot.v11.message import Message
from nonebot.plugin import on_startswith
from nonebot.rule import to_me
import json
import nonebot
import os
import re

from .plugin_state import checkAllow, checkOn, getPlugins


def to_pinyin(s):
    from itertools import chain
    from pypinyin import pinyin, Style

    return "".join(chain.from_iterable(pinyin(s, style=Style.TONE3)))


helper = on_startswith(msg="帮助", rule=to_me(), priority=1, block=True)


@helper.handle()
async def _(event: Event):
    if event.get_user_id() in nonebot.get_driver().config.other_bots:
        return
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
        message = "插件列表:"
        plugin_names = sorted(plugins.keys(), key=to_pinyin)
        for p in plugin_names:
            if checkAllow(isGroupMessage, p, _id):
                if checkOn(isGroupMessage, p, _id):
                    message += f"\n|O| {p}"
                else:
                    message += f"\n|X| {p}"
        message += '\n--使用"帮助 PLUGIN_NAME"获取更多信息\n--使用"开启/关闭 PLUGIN_NAME"开启或关闭插件'
        await helper.finish(Message(message))
    else:
        message = msg
        if msg not in plugins:
            message += "不在插件列表"
        else:
            if checkAllow(isGroupMessage, msg, _id):
                if checkOn(isGroupMessage, msg, _id):
                    message += f' [ON]:\n{plugins[msg]["desc"]}'
                else:
                    message += f' [OFF]:\n{plugins[msg]["desc"]}'
            else:
                message += "未启用"
        await helper.finish(Message(message))
