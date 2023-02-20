from nonebot.adapters.onebot.v11 import Bot, Event, GroupMessageEvent, MessageSegment
from nonebot.adapters.onebot.v11.message import Message
from nonebot.matcher import Matcher
from nonebot.plugin import on_keyword
import datetime
import hashlib
import json
import nonebot
import os
import re
import requests
import time
import timeout_decorator
import urllib

from ..plugin_manager.plugin_state import checkAllow, checkOn


def isZH(s: str) -> bool:
    try:
        j = requests.get("https://fanyi.baidu.com/langdetect?query=" + urllib.parse.quote(s)).json()
        if j["lan"] == "zh":
            return True
        return False
    except:
        zh = 0
        l = len(s)
        for c in s:
            if "\u4e00" <= c <= "\u9fa5":
                zh += 1
                if zh * 4 >= l * 3:
                    return True
        return False


def getMonth() -> str:
    return datetime.datetime.now().strftime("%Y%m")


def getUsage(m: str = getMonth()) -> int:
    with open(os.path.dirname(__file__) + "/usage.json", "r") as f:
        usage = json.load(f)
        if m in usage:
            return usage[m]
        else:
            return 0


def setUsage(u: int, m: str = getMonth()) -> None:
    usage: json
    with open(os.path.dirname(__file__) + "/usage.json", "r") as f:
        usage = json.load(f)
    usage[m] = u
    with open(os.path.dirname(__file__) + "/usage.json", "w") as f:
        json.dump(usage, f)


@timeout_decorator.timeout(7)
def getTranslate(s: str, f: str, t: str) -> json:
    setUsage(getUsage() + len(s))
    appid = "YOUR_APPID"
    s = str(s)
    salt = str(int(time.time()))
    key = "YOUR_KEY"
    sign = hashlib.md5((appid + s + salt + key).encode("utf-8")).hexdigest()
    return requests.get(f"http://api.fanyi.baidu.com/api/trans/vip/translate?q={urllib.parse.quote(s)}&from={f}&to={t}&appid={appid}&salt={salt}&sign={sign}").json()


translater = on_keyword("译", priority=10, block=False)
translate_dict = {
    "": "auto",
    "简体中文": "zh",
    "中文": "zh",
    "简中": "zh",
    "汉语": "zh",
    "汉文": "zh",
    "简汉": "zh",
    "简": "zh",
    "中": "zh",
    "汉": "zh",
    "英语": "en",
    "英文": "en",
    "英": "en",
    "粤语": "yue",
    "粤": "yue",
    "文言文": "wyw",
    "文言": "wyw",
    "文": "wyw",
    "日语": "jp",
    "日文": "jp",
    "日": "jp",
    "韩语": "kor",
    "韩文": "kor",
    "韩": "kor",
    "法语": "fra",
    "法文": "fra",
    "法": "fra",
    "西班牙语": "spa",
    "西": "spa",
    "泰语": "th",
    "泰": "th",
    "阿拉伯语": "ara",
    "阿": "ara",
    "俄语": "ru",
    "俄文": "ru",
    "俄": "ru",
    "葡萄牙语": "pt",
    "葡": "pt",
    "德语": "de",
    "德文": "de",
    "德": "de",
    "意大利语": "it",
    "意": "it",
    "希腊语": "el",
    "希": "el",
    "荷兰语": "nl",
    "荷": "nl",
    "波兰语": "pl",
    "波": "pl",
    "保加利亚语": "bul",
    "保": "bul",
    "爱沙尼亚语": "est",
    "爱": "est",
    "丹麦语": "dan",
    "丹": "dan",
    "芬兰语": "fin",
    "芬": "fin",
    "捷克语": "cs",
    "捷": "cs",
    "罗马尼亚语": "rom",
    "罗": "rom",
    "斯洛文尼亚语": "slo",
    "斯": "slo",
    "瑞典语": "swe",
    "瑞": "swe",
    "匈牙利语": "hu",
    "匈": "hu",
    "繁体中文": "cht",
    "繁中": "cht",
    "繁": "cht",
    "越南语": "vie",
    "越": "vie",
}


@translater.handle()
async def _(event: Event, matcher: Matcher):
    if event.get_user_id() in nonebot.get_driver().config.other_bots:
        return
    plugin_name = "翻译"
    isGroup = True if event.get_event_name() == "message.group.normal" else False
    _id = str(event.group_id if isGroup else event.user_id)
    if not checkAllow(isGroup, plugin_name, _id):
        return
    if not checkOn(isGroup, plugin_name, _id):
        return
    msg = str(event.get_message())
    if (len(msg) < 4) or (" " not in msg) or (msg[0] == " "):
        return
    s = ""
    f = "auto"
    t = "zh"
    cmd = msg.split(" ")[0]
    s = msg[len(cmd) + 1 :]
    if cmd == "翻译":
        f = "auto"
        t = "en" if isZH(s) else "zh"
    elif "翻译" in cmd:
        ft = re.sub("翻译(?:成|到|为|)", "|", "-" + cmd + "-").split("|")
        f = ft[0][1:]
        t = ft[1][:-1]
        if (f not in translate_dict) or (t not in translate_dict):
            return
        f = translate_dict[f]
        t = translate_dict[t]
        if t == "auto":
            matcher.stop_propagation()
            await translater.finish("目标语言不可省略")
    elif len(cmd) == 3 and cmd[1] == "译":
        f = cmd[0]
        t = cmd[2]
        if (f not in translate_dict) or (t not in translate_dict):
            return
        f = translate_dict[f]
        t = translate_dict[t]
    else:
        s = ""
    if s == "":
        return
    matcher.stop_propagation()
    try:
        ret = getTranslate(s, f, t)
    except:
        await translater.finish(Message("翻译请求超时, 请稍后再试"))
    if "error_code" in ret:
        await translater.finish(f'翻译失败 [{ret["error_code"]}: {ret["error_msg"]}]')
    await translater.finish(f'{ret["from"]}->{ret["to"]}:\n{ret["trans_result"][0]["dst"]}')
