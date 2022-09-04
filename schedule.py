import datetime
import nonebot
import json
import requests
from nonebot import require
from .db import connect_redis
from .config import jx3_config

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler


def request(uri, data):
    host = jx3_config.jx3api_host
    # 访问http接口
    url = host + uri
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    # 发送请求
    res = requests.post(url, headers=headers, data=json.dumps(data))
    # 获取返回数据
    res_json = res.json()
    return res_json


async def server_check():
    server = jx3_config.server
    week = datetime.datetime.now().weekday()
    # 只有周一和周四触发
    if week not in [0, 3, 5]:
        return
    # 7点前不触发
    if datetime.datetime.now().hour < 7:
        return
    cacheKey = "jx3_server_status:%s-%s"
    r = connect_redis()
    isStart = r.get(cacheKey % (server, week))
    if isStart:
        return

    res = request("/app/check", {"server": "乾坤一掷"})
    status = 0
    msg = "【开服提醒】\n服务器：乾坤一掷\n"
    if res["code"] == 200:
        status = res["data"]["status"]
    if status == 1:
        msg += "服务器开服啦！！！记得点天工树！！！"
        bot = nonebot.get_bot()
        r.set(cacheKey % (server, week), 1)
        r.expire(cacheKey % (server, week), 60 * 60 * 24)
        await bot.send_private_msg(user_id=724148501, message=msg)
    pass


scheduler.add_job(server_check, "cron", second="*/10")
