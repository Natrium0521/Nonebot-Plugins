from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.plugin import on_startswith
import json
import re
import requests
import timeout_decorator
import urllib

from .bili_tool import is_on, no_bot

on_hs = on_startswith({"B站热搜", "b站热搜"}, rule=Rule(no_bot, is_on), priority=10, block=False)


@timeout_decorator.timeout(5)
def getHotSearch() -> json:
    return requests.get("https://api.bilibili.com/x/web-interface/search/square?limit=50").json()


@on_hs.handle()
async def _(event: Event, matcher: Matcher):
    msg = re.sub(" ", "", str(event.get_message())[4:])
    if (not msg.isdigit()) and (msg != "") and (msg != "全"):
        return
    matcher.stop_propagation()
    sid = -1 if msg == "全" else int("0" + msg)
    hsj: json
    try:
        hsj = getHotSearch()
    except:
        await on_hs.finish("B站热搜获取失败或超时, 请稍后再试")
    if hsj["code"]:
        await on_hs.finish(f'B站热搜获取失败, code: {hsj["code"]}')
    hsl = hsj["data"]["trending"]["list"]
    if sid > len(hsl):
        await on_hs.finish(f"当前热搜只有{len(hsl)}条")
    if sid > 0:
        await on_hs.finish(f'当前热搜第{sid}条:\n{hsl[sid-1]["show_name"]}\nhttps://search.bilibili.com/all?keyword={urllib.parse.quote(hsl[sid-1]["keyword"])}')
    message = "当前B站热搜:"
    cnt = len(hsl) if sid else min(10, len(hsl))
    for i in range(cnt):
        message += f'\n{i+1}: {hsl[i]["show_name"]}'
    await on_hs.finish(message)
