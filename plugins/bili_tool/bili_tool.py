from nonebot.adapters import Event
from nonebot.plugin import on_fullmatch
from nonebot.rule import Rule
import json
import nonebot
import os

from ..plugin_manager.plugin_state import checkAllow, checkOn


async def no_bot(event: Event) -> bool:
    if event.get_user_id() in nonebot.get_driver().config.other_bots:
        return False
    return True


async def is_on(event: Event) -> bool:
    plugin_name = "bili_tool"
    isGroup = True if event.get_event_name() == "message.group.normal" else False
    _id = str(event.group_id if isGroup else event.user_id)
    if not checkAllow(isGroup, plugin_name, _id):
        return False
    if not checkOn(isGroup, plugin_name, _id):
        return False
    return True


def getScheduled() -> json:
    with open(os.path.dirname(__file__) + "/scheduled_weekly.json", "r") as f:
        return json.load(f)


def setScheduled(scheduled: json) -> None:
    with open(os.path.dirname(__file__) + "/scheduled_weekly.json", "w") as f:
        json.dump(scheduled, f)
    return


def clearCache() -> None:
    for f in os.listdir(os.path.dirname(__file__) + "/cache/"):
        os.remove(os.path.dirname(__file__) + "/cache/" + f)
    return


on_wk = on_fullmatch({"订阅每周必看", "取消订阅每周必看"}, rule=Rule(no_bot, is_on), priority=10, block=True)


@on_wk.handle()
async def _(event: Event):
    msg = str(event.get_message())
    isGroup = True if event.get_event_name() == "message.group.normal" else False
    _id = str(event.group_id if isGroup else event.user_id)
    _type = "groups" if isGroup else "users"
    scheduled = getScheduled()
    if msg == "订阅每周必看":
        if _id not in scheduled[_type]:
            scheduled[_type].append(_id)
    elif msg == "取消订阅每周必看":
        if _id in scheduled[_type]:
            scheduled[_type].remove(_id)
    setScheduled(scheduled)
    await on_wk.finish("已" + ("取消订阅" if msg[:2] == "取消" else "订阅"))
