from nonebot.adapters import Event, Bot
from nonebot.adapters.onebot.v11 import Message
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.plugin import on_startswith
import json
import re
import requests
import timeout_decorator

from .bili_tool import no_bot, is_on

on_weekly = on_startswith({"每周必看"}, rule=Rule(no_bot, is_on), priority=10, block=False)


@timeout_decorator.timeout(10)
def json2messages(j: json) -> list:
    vconfig = j["data"]["config"]
    vlist = j["data"]["list"]
    messages = [{"type": "node", "data": {"name": f'每周必看 {vconfig["number"]}', "uin": "104502494", "content": f'{vconfig["name"]}\n{vconfig["subject"]} | {vconfig["label"]}'}}]
    for v in vlist:
        messages.append(
            {
                "type": "node",
                "data": {
                    "name": f'每周必看 {vconfig["number"]}',
                    "uin": "104502494",
                    "content": f'{v["title"]}\n[CQ:image,file={v["pic"]}]\n{v["short_link"]}\nUP: {v["owner"]["name"]}\n播放: {v["stat"]["view"]}\n推荐理由: {v["rcmd_reason"]}',
                },
            }
        )
    messages.append({"type": "node", "data": {"name": f'每周必看 {vconfig["number"]}', "uin": "104502494", "content": j["data"]["reminder"]}})
    return messages


@on_weekly.handle()
async def _(event: Event, matcher: Matcher, bot: Bot):
    msg = re.sub(" ", "", str(event.get_message())[4:])
    if (not msg.isdigit()) and (msg != ""):
        return
    matcher.stop_propagation()
    wid = int("0" + msg)
    wl: json
    try:
        wids = requests.get("https://api.bilibili.com/x/web-interface/popular/series/list").json()
        if wids["code"]:
            await on_weekly.finish(f'每周必看获取失败, code: {wids["code"]}')
        if wid == 0:
            wid = wids["data"]["list"][0]["number"]
        elif wid > wids["data"]["list"][0]["number"]:
            await on_weekly.finish(f'每周必看第{wid}期不存在, 最新一期为{wids["data"]["list"][0]["number"]}')
        wl = requests.get(f"https://api.bilibili.com/x/web-interface/popular/series/one?number={wid}").json()
        if wl["code"]:
            await on_weekly.finish(f'第{wid}期每周必看获取失败, code: {wl["code"]}')
    except:
        await on_weekly.finish("网络错误, 请稍后再试")
    messages = json2messages(wl)
    if event.get_event_name() == "message.group.normal":
        await bot.call_api("send_group_forward_msg", **{"group_id": event.group_id, "messages": messages})
    else:
        await bot.call_api("send_private_forward_msg", **{"user_id": event.user_id, "messages": messages})
