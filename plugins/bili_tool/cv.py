from nonebot.adapters import Event
from nonebot.adapters.onebot.v11 import Message, MessageSegment
from nonebot.matcher import Matcher
from nonebot.rule import Rule
from nonebot.plugin import on_keyword
import bs4
import imgkit
import json
import os
import re
import requests
import timeout_decorator

from .bili_tool import no_bot, is_on

on_cv = on_keyword({"CV", "cv"}, rule=Rule(no_bot, is_on), priority=12, block=False)


@timeout_decorator.timeout(10)
def article2pic(article: str, cv: str) -> str:
    path = os.path.dirname(__file__) + f"/cache/{cv}.jpg"
    imgkit.from_string(article, path, css=os.path.dirname(__file__) + "/src/bilibili-article-web.css")
    return path


@on_cv.handle()
async def _(event: Event, matcher: Matcher):
    msg = str(event.get_message()).lower()
    cvs = re.compile("cv\d+").findall(msg)
    if len(cvs) == 0:
        return
    cv = cvs[0]
    isSingleCV = True if cv == msg else False
    html = ""
    try:
        html = requests.get(f"https://www.bilibili.com/read/{cv}").content.decode("utf-8")
    except:
        if isSingleCV:
            matcher.stop_propagation()
            await on_cv.finish(f"failed to GET https://www.bilibili.com/read/{cv}")
        return
    bs = bs4.BeautifulSoup(html, "html.parser")
    article = ""
    try:
        article = str(bs.select(".article-container")[0])
    except:
        if isSingleCV:
            matcher.stop_propagation()
            await on_cv.finish(f"{cv}不存在或被删除")
        return
    matcher.stop_propagation()
    if "read-article-holder" not in str(bs.select(".article-content")[0]):
        scripts = bs.select("script")
        s = ""
        for ss in scripts:
            if "__INITIAL_STATE__" in str(ss):
                s = str(ss)
                break
        c = re.compile('"content".*"keywords"').findall(s)[0][11:-12]
        c = re.sub("&#34;", '"', c)
        final = ""
        if "ops" in c:
            j = json.loads(c)
            for i in j["ops"]:
                p = "<p"
                if "attributes" in i:
                    for a in i["attributes"]:
                        p += f' {a}="{i["attributes"][a]}"'
                p = p + ">{}</p>"
                if type(i["insert"]) == str:
                    final += p.format(i["insert"])
                    continue
                if "native-image" in i["insert"]:
                    _ = {"url": "src", "width": "width", "height": "height", "alt": "alt"}
                    im = "<img"
                    for __ in _:
                        if __ in i["insert"]["native-image"]:
                            im += f' {_[__]}="{i["insert"]["native-image"][__]}"'
                    im += ">"
                    final += p.format(im)
        else:
            final = c
        final = re.sub(r"\\\\n", "<br>", final)
        article = re.sub(
            '<div .*article-content" .*article-content">(?:.|\n)*?<\/div>',
            f'<div id="article-content" class="article-content"><div id="read-article-holder" class="normal-article-holder read-article-holder">{final}</div></div>',
            article,
        )
    article = re.sub('data-src="//i0.hdslb.com', 'src="https://i0.hdslb.com', article)
    article = re.sub("data-src", "src", article)
    j = requests.get(f"https://api.bilibili.com/x/article/viewinfo?id={cv[2:]}&mobi_app=pc&from=web").json()
    article = re.sub("--阅读", f'{j["data"]["stats"]["view"]}阅读', article)
    article = re.sub("--喜欢", f'{j["data"]["stats"]["like"]}喜欢', article)
    article = re.sub("--评论", f'{j["data"]["stats"]["reply"]}评论', article)
    article = re.sub('<div class="card-image__image".*?<\/div>', f'<img src="{j["data"]["banner_url"]}" width="660" height="370">', article)
    u = requests.get(f'https://api.bilibili.com/x/web-interface/card?mid={j["data"]["mid"]}&article=true').json()
    article = re.sub(
        '<div class="avatar-container.*?<\/div>',
        f'<div class="avatar-container" data-v-904253a6=""><a><div class="bili-avatar" style="width: 100%;height:100%;"><img src="{u["data"]["card"]["face"]}" width="44" height="44"></div></a></div>',
        article,
    )
    path = ""
    try:
        path = article2pic(article, cv)
    except:
        await on_cv.finish(f"{cv}图片生成失败或超时")
        return
    await on_cv.finish(MessageSegment.image("file:///" + path) + Message("\n详戳: https://www.bilibili.com/read/" + cv))
