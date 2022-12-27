from nonebot.plugin import on_startswith
from nonebot.matcher import Matcher
from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.message import Message
import nonebot
import urllib

from ..plugin_manager.plugin_state import checkAllow, checkOn

searcher = on_startswith({"百度", "baidu", "csdn", "CSDN", "必应", "Bing", "bing"}, priority=20, block=True)
searcher_dict = {
    "百度": "https://www.baidu.com/s?wd={}",
    "baidu": "https://www.baidu.com/s?wd={}",
    "csdn": "https://so.csdn.net/so/search?q={}",
    "CSDN": "https://so.csdn.net/so/search?q={}",
    "必应": "https://cn.bing.com/search?q={}&ensearch=0",
    "bing": "https://cn.bing.com/search?q={}&ensearch=1",
    "Bing": "https://cn.bing.com/search?q={}&ensearch=1",
}


@searcher.handle()
async def _(event: Event, matcher: Matcher):
    if event.get_user_id() in nonebot.get_driver().config.other_bots:
        return
    plugin_name = "懒狗搜索"
    isGroup = True if event.get_event_name() == "message.group.normal" else False
    _id = str(event.group_id if isGroup else event.user_id)
    if not checkAllow(isGroup, plugin_name, _id):
        return
    if not checkOn(isGroup, plugin_name, _id):
        return
    msg = str(event.get_message())
    message = ""
    for i in range(5, 0, -1):
        if msg[:i] in searcher_dict:
            message = searcher_dict[msg[:i]].format(str(urllib.parse.quote(msg[i:])))
            break
    await searcher.finish(message)
