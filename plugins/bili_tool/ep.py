from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.plugin import on_keyword
import bs4
import re
import requests

from .bili_tool import no_bot, is_on
from .bv import bv2message

on_ep = on_keyword({"EP", "ep"}, rule=Rule(no_bot, is_on), priority=12, block=False)


@on_ep.handle()
async def _(event: Event, matcher: Matcher):
    msg = str(event.get_message())
    eps = re.compile("(?:ep|EP)\d+").findall(msg)
    if len(eps) == 0:
        return
    ep = eps[0].lower()
    isSingleEP = True if ep == msg else False
    html = ""
    try:
        html = requests.get(f"https://www.bilibili.com/bangumi/play/{ep}").content.decode("utf-8")
    except:
        if isSingleEP:
            matcher.stop_propagation()
            await on_ep.finish(f"failed to GET https://www.bilibili.com/bangumi/play/{ep}")
        return
    bs = bs4.BeautifulSoup(html, "html.parser")
    ss = bs.select("script")
    bv = ""
    for s in ss:
        if "__INITIAL_STATE__" in str(s):
            a = re.findall(f'BV.*?,"id":{ep[2:]}', str(s))[0]
            bv = re.findall("BV.{10}", a)[-1]
            break
    if bv == "":
        if isSingleEP:
            matcher.stop_propagation()
            await on_ep.finish(f"{ep}不存在")
        return
    matcher.stop_propagation()
    message: Message
    try:
        message = bv2message(bv)
    except:
        await on_ep.finish(f"{bv}信息获取失败或超时, 请稍后再试")
    await on_ep.finish(message)
