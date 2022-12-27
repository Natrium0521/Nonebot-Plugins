from nonebot import require, get_driver
from nonebot.adapters import Bot
from nonebot.adapters.onebot.v11 import MessageSegment
import datetime

from .daily_news import getScheduled, getPic


scheduler = require("nonebot_plugin_apscheduler").scheduler


@scheduler.scheduled_job("cron", hour=2, minute=0)
async def _():
    today = datetime.date.today()
    bot = get_driver().bots["104502494"]
    scheduled = getScheduled()
    p: str
    try:
        p = getPic()
    except:
        return
    for g in scheduled["groups"]:
        await bot.send_msg(message_type="group", group_id=int(g), message=MessageSegment.image("file:///" + p))
    for u in scheduled["users"]:
        await bot.send_msg(message_type="private", user_id=int(u), message=MessageSegment.image("file:///" + p))
