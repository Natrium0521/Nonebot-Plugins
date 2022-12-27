from nonebot.plugin import on_message
from nonebot.adapters.onebot.v11 import GroupMessageEvent
import random
import time

from ..plugin_manager.plugin_state import checkAllow, checkOn

repeater = on_message(priority=100)
random.seed(int(time.time()))
cd = {}


@repeater.handle()
async def handle_repeater(event: GroupMessageEvent):
    plugin_name = "复读坤"
    gid = str(event.group_id)
    if not checkAllow(True, plugin_name, gid):
        return
    if not checkOn(True, plugin_name, gid):
        return
    global cd
    if gid not in cd:
        cd[gid] = 0
    cd[gid] += 1
    a = random.randint(1, 20000)
    if a <= 233:
        if cd[gid] > 17 and (("subType=1" in str(event.get_message())) or ((len(str(event.get_message())) <= 20) and ("CQ:" not in str(event.get_message())))):
            cd[gid] = 0
            await repeater.send(event.get_message())
