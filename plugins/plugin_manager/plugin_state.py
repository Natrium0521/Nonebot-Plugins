import json
import os


def getPlugins() -> json:
    plugins: json
    with open(os.path.dirname(__file__) + "/plugins.json", "r") as f:
        plugins = json.load(f)
    return plugins


def setPlugins(plugins: json) -> None:
    with open(os.path.dirname(__file__) + "/plugins.json", "w") as f:
        json.dump(plugins, f, ensure_ascii=False)
    return


def checkAllow(isGroup: bool, plugin: str, _id: str) -> bool:
    plugins = getPlugins()
    allow = "allow_group" if isGroup else "allow_user"
    ban = "ban_group" if isGroup else "ban_user"
    if (len(plugins[plugin][ban]) == 0) or (_id in plugins[plugin][allow]):
        return True
    elif "all" in plugins[plugin][allow]:
        if _id not in plugins[plugin][ban]:
            return True
    return False


def checkOn(isGroup: bool, plugin: str, _id: str) -> bool:
    plugins = getPlugins()
    on = "on_group" if isGroup else "on_user"
    off = "off_group" if isGroup else "off_user"
    if (len(plugins[plugin][off]) == 0) or (_id in plugins[plugin][on]):
        return True
    elif "all" in plugins[plugin][on]:
        if _id not in plugins[plugin][off]:
            return True
    return False


def checkManager(plugin: str, uid: str) -> bool:
    return False
