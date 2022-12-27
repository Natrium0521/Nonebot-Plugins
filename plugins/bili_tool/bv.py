from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.plugin import on_keyword
import json
import re
import requests
import time
import timeout_decorator

from .bili_tool import no_bot, is_on

on_bv = on_keyword({"BV", "bv"}, rule=Rule(no_bot, is_on), priority=10, block=False)


@timeout_decorator.timeout(10)
def bv2message(bv: str, part: int = 0) -> Message:
    cidjson = requests.get(f"https://api.bilibili.com/x/player/pagelist?bvid={bv}").json()
    if cidjson["code"] != 0:
        return Message(f"{bv}不存在")
    cid = cidjson["data"][0]["cid"]
    picjson = requests.get(f"https://api.bilibili.com/x/web-interface/view?cid={cid}&bvid={bv}").json()
    if picjson["code"] != 0:
        return Message("未知错误 请稍后再试")
    title = picjson["data"]["title"]
    allp = len(picjson["data"]["pages"])
    nlnk = "https://www.bilibili.com/video/" + bv
    if allp != 1 and part:
        nlnk += "?p=" + str(part)
        try:
            title += f'\nP{part} {picjson["data"]["pages"][part - 1]["part"]}'
        except IndexError:
            return Message(f"Part{part}不存在")
    coverlink = picjson["data"]["pic"]
    pubdate = picjson["data"]["pubdate"]
    upper = picjson["data"]["owner"]["name"]
    like = picjson["data"]["stat"]["like"]
    coin = picjson["data"]["stat"]["coin"]
    fav = picjson["data"]["stat"]["favorite"]
    share = picjson["data"]["stat"]["share"]
    reply = picjson["data"]["stat"]["reply"]
    danmaku = picjson["data"]["stat"]["danmaku"]
    view = picjson["data"]["stat"]["view"]
    upt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(pubdate)))
    message = Message(f"{title}\n")
    message += MessageSegment.image(coverlink)
    message += Message(f"\n{nlnk}\nUP: {upper}\n上传时间: {upt}\n播放量: {view}\n点赞: {like}\n投币: {coin}\n收藏: {fav}\n分享: {share}\n评论: {reply}\n弹幕: {danmaku}")
    return message


@on_bv.handle()
async def _(event: Event, matcher: Matcher):
    msg = str(event.get_message())
    bvs = re.compile("(?:bv|BV)[0-9a-zA-Z]{10}").findall(msg)
    if len(bvs) == 0:
        return
    matcher.stop_propagation()
    bv = bvs[0]
    part = 0
    ps = re.compile("(?:\?|&)p=\d+").findall(msg)
    if len(ps):
        part = int(ps[0][3:])
    message: Message
    try:
        message = bv2message(bv, part)
    except:
        await on_bv.finish(f"{bv}信息获取失败或超时, 请稍后再试")
    await on_bv.finish(message)
