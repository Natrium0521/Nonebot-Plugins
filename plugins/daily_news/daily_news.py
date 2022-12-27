from nonebot.adapters.onebot.v11 import MessageSegment, Event
from nonebot.plugin import on_fullmatch
import nonebot
import datetime
import imghdr
import json
import os
import requests
import timeout_decorator


from ..plugin_manager.plugin_state import checkAllow, checkOn


def getScheduled() -> json:
    with open(os.path.dirname(__file__) + "/scheduled.json", "r") as f:
        return json.load(f)


def setScheduled(scheduled: json) -> None:
    with open(os.path.dirname(__file__) + "/scheduled.json", "w") as f:
        json.dump(scheduled, f)
    return


def clearCache() -> None:
    for f in os.listdir(os.path.dirname(__file__) + "/cache/"):
        os.remove(os.path.dirname(__file__) + "/cache/" + f)
    return


@timeout_decorator.timeout(7)
def getPic() -> str:
    if datetime.date.today().day == 1:
        clearCache()
    p = requests.get("https://api.03c3.cn/zb").content
    path = os.path.dirname(__file__) + f"/cache/tmp.png"
    with open(path, "wb") as f:
        f.write(p)
    if imghdr.what(path) == None:
        raise
    path = os.path.dirname(__file__) + f"/cache/{datetime.date.today()}.png"
    with open(path, "wb") as f:
        f.write(p)
    return path


dailynews = on_fullmatch({"今日新闻", "/今日新闻", "订阅今日新闻", "取消订阅今日新闻"}, priority=10, block=True)


@dailynews.handle()
async def _(event: Event):
    if event.get_user_id() in nonebot.get_driver().config.other_bots:
        return
    plugin_name = "今日新闻"
    isGroup = True if event.get_event_name() == "message.group.normal" else False
    _id = str(event.group_id if isGroup else event.user_id)
    if not checkAllow(isGroup, plugin_name, _id):
        return
    if not checkOn(isGroup, plugin_name, _id):
        return
    msg = str(event.get_message())
    path = os.path.dirname(__file__) + f"/cache/{datetime.date.today()}.png"
    if msg == "今日新闻":
        if not os.path.isfile(path):
            try:
                getPic()
            except:
                await dailynews.finish("今日新闻获取失败或超时, 请稍后再试")
        await dailynews.finish(MessageSegment.image(f"file:///{path}"))
    elif msg == "/今日新闻":
        try:
            getPic()
        except:
            await dailynews.finish("今日新闻更新失败或超时, 请稍后再试")
        await dailynews.finish(MessageSegment.image(f"file:///{path}"))
    _type = "groups" if isGroup else "users"
    scheduled = getScheduled()
    if msg == "订阅今日新闻":
        if _id not in scheduled[_type]:
            scheduled[_type].append(_id)
    elif msg == "取消订阅今日新闻":
        if _id in scheduled[_type]:
            scheduled[_type].remove(_id)
    setScheduled(scheduled)
    await dailynews.finish("已" + ("取消订阅" if msg[:2] == "取消" else "订阅"))
