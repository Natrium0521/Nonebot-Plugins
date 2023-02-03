from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.plugin import on_keyword
import re
import requests

from .bili_tool import no_bot, is_on
from .bv import bv2message

on_b23 = on_keyword({"b23.tv/"}, rule=Rule(no_bot, is_on), priority=11, block=False)


@on_b23.handle()
async def _(event: Event, matcher: Matcher):
    msg = str(event.get_message())
    b23s = re.compile("b23.tv/[0-9a-zA-Z]{7}").findall(msg)
    if len(b23s) == 0:
        return
    matcher.stop_propagation()
    b23 = b23s[0]
    bvr = requests.get("https://" + b23, allow_redirects=False)
    bv = ""
    try:
        msg = bvr.headers["Location"]
        bv = re.compile("BV[0-9a-zA-Z]{10}").findall(msg)[0]
    except:
        await on_b23.finish("b23短链不存在或是直播间链接")
    part = 0
    ps = re.compile("(?:\?|&)p=\d+").findall(msg)
    if len(ps):
        part = int(ps[0][3:])
    message: Message
    try:
        message = bv2message(bv, part)
    except:
        await on_b23.finish(f"{bv}信息获取失败或超时, 请稍后再试")
    await on_b23.finish(message)
