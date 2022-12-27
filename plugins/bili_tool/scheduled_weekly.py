from nonebot import require, get_driver
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import MessageSegment
import datetime
import json
import requests

from .bili_tool import getScheduled
from .weekly import json2messages

scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", hour=18, minute=30)
async def _():
    if datetime.date.today().weekday() != 4:
        return
    wl: json
    try:
        wids = requests.get("https://api.bilibili.com/x/web-interface/popular/series/list").json()
        if wids["code"]:
            return
        wid = wids["data"]["list"][0]["number"]
        wl = requests.get(f"https://api.bilibili.com/x/web-interface/popular/series/one?number={wid}").json()
        if wl["code"]:
            return
    except:
        return
    bot = get_driver().bots["104502494"]
    scheduled = getScheduled()
    messages = json2messages(wl)
    for g in scheduled["groups"]:
        await bot.call_api("send_group_forward_msg", **{"group_id": g, "messages": messages})
    for u in scheduled["users"]:
        await bot.call_api("send_private_forward_msg", **{"user_id": u, "messages": messages})
