from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.plugin import on_startswith
import cv2
import nonebot
import os
import qrcode
import re
import requests
import time

from ..plugin_manager.plugin_state import checkAllow, checkOn

CACHE_PATH = os.path.dirname(__file__) + "/cache/"


def clearCache() -> None:
    for f in os.listdir(CACHE_PATH):
        os.remove(CACHE_PATH + f)
    return


def qrEncode(s: str) -> Message:
    try:
        img = qrcode.make(s)
        img_name = time.time()
        img.save(CACHE_PATH + f"{img_name}.jpg")
        return MessageSegment.image(f"file:///{CACHE_PATH}{img_name}.jpg")
    except:
        return Message("二维码生成失败")


def qrDecode(s: str) -> Message:
    depro = CACHE_PATH + "../src/detect.prototxt"
    decaf = CACHE_PATH + "../src/detect.caffemodel"
    srpro = CACHE_PATH + "../src/sr.prototxt"
    srcaf = CACHE_PATH + "../src/sr.caffemodel"
    detector = cv2.wechat_qrcode_WeChatQRCode(depro, decaf, srpro, srcaf)
    img = cv2.imread(s)
    res, points = detector.detectAndDecode(img)
    if len(res) == 0:
        return Message("未识别出二维码")
    for i in range(len(points)):
        pos = points[i]
        color = (0, 0, 255)
        thick = 3
        for p in [(0, 1), (1, 2), (2, 3), (3, 0)]:
            start = int(pos[p[0]][0]), int(pos[p[0]][1])
            end = int(pos[p[1]][0]), int(pos[p[1]][1])
            cv2.line(img, start, end, color, thick)
        if len(res) > 1:
            cv2.putText(img, f"No.{i+1}", (int(pos[0][0]), int(pos[0][1]) - 3), cv2.FONT_ITALIC, 1, color, thick)
    new_path = CACHE_PATH + f"{time.time()}.jpg"
    cv2.imwrite(new_path, img)
    message = Message("识别结果:\n") + MessageSegment.image(f"file:///{new_path}")
    if len(res) == 1:
        return message + Message("\n" + res[0])
    for i in range(len(res)):
        message += Message(f"\nNo.{i+1}: {res[i]}")
    return message


qr = on_startswith({"qr", "QR"}, priority=10, block=True)


@qr.handle()
async def _(event: Event, matcher: Matcher):
    if event.get_user_id() in nonebot.get_driver().config.other_bots:
        return
    plugin_name = "qrcode_tool"
    isGroup = True if event.get_event_name() == "message.group.normal" else False
    _id = str(event.group_id if isGroup else event.user_id)
    if not checkAllow(isGroup, plugin_name, _id):
        return
    if not checkOn(isGroup, plugin_name, _id):
        return
    if int(time.time()) % 10 == 7:
        clearCache()
    msg = str(event.get_message())[2:]
    imgs = re.compile("\[CQ:image,file=.*\.image.*url=.*gchat\.qpic\.cn.*\]").findall(msg)
    if not len(imgs):
        await qr.finish(qrEncode(msg))
    for img in imgs:
        url = re.compile("url=https.*?;").findall(img)[0][4:-1]
        img_path = CACHE_PATH + f"{time.time()}.jpg"
        with open(img_path, "wb") as f, requests.get(url) as r:
            f.write(r.content)
        await qr.send(qrDecode(img_path))
