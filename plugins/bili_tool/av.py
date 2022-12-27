from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.plugin import on_keyword
import json
import re
import requests

from .bili_tool import no_bot, is_on
from .bv import bv2message

on_av = on_keyword({"AV", "av"}, rule=Rule(no_bot, is_on), priority=12, block=False)


@on_av.handle()
async def _(event: Event, matcher: Matcher):
    msg = str(event.get_message())
    avs = re.compile("(?:av|AV)\d+").findall(msg)
    if len(avs) == 0:
        return
    av = avs[0]
    isSingleAv = True if av == msg else False
    a2bjson = requests.get(f"https://api.bilibili.com/x/web-interface/view?aid={av[2:]}").json()
    if a2bjson["code"]:
        if isSingleAv:
            matcher.stop_propagation()
            await on_av.finish(f"{av}不存在")
        return
    matcher.stop_propagation()
    bv = a2bjson["data"]["bvid"]
    part = 0
    ps = re.compile("(?:\?|&)p=\d+").findall(msg)
    if len(ps):
        part = int(ps[0][3:])
    message: Message
    try:
        message = bv2message(bv, part)
    except:
        await on_av.finish(f"{bv}信息获取失败或超时, 请稍后再试")
    await on_av.finish(message)
