# -*- coding: UTF-8 -*-
import json
import requests
import datetime
import os
from nonebot import on_keyword, on_regex
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent
from nonebot.params import RegexMatched
from .config import jx3_config, jx3_profession_config
from .schedule import server_check
from matplotlib import pyplot as plt, font_manager
import imgkit

# plt显示中文
# TODO 按系统适配
# plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
# plt.rcParams['image.interpolation'] = 'nearest'
# plt.rcParams['image.cmap'] = 'gray'
font = font_manager.FontProperties(fname=os.path.dirname(os.path.abspath(__file__)) + '/fonts/plt.ttf')
plt.rcParams['axes.unicode_minus'] = False


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


# [日常][查询日常][日常查询] [可选参数：服务器名]
daily = on_regex(r"^(日常|查询日常|日常查询)(\s[\u4e00-\u9fa5]+)*$", priority=5, block=True)
# [金价][查询金价][金价查询] [可选参数：服务器名]
gold = on_regex(r"^(金价|查询金价|金价查询)(\s[\u4e00-\u9fa5]+)*$", priority=5, block=True)
# [小药][查询小药][小药查询] [可选参数：心法名]
medicine = on_regex(r"^(小药|查询小药|小药查询)(\s[\u4e00-\u9fa5]+)*$", priority=5, block=True)
# [宏][查询宏][宏查询] [必选参数：心法名]
macro = on_regex(r"^(宏|查询宏|宏查询)(\s[\u4e00-\u9fa5]+)+$", priority=5, block=True)
# [配装][查询配装][配装查询] [必选参数：心法名]
equip = on_regex(r"^(配装|查询配装|配装查询)(\s[\u4e00-\u9fa5]+)+$", priority=5, block=True)
# [骚话]
random = on_keyword({"骚话"}, priority=5, block=True)


# 查询日常
@daily.handle()
async def daily_handle(event: MessageEvent, args: str = RegexMatched()):
    # 获取参数
    args = args.split()
    if len(args) == 1:
        server = jx3_config.server
    else:
        server = args[1]
    res = request("/app/daily", {"server": server})
    msg = ""
    if res["code"] == 200:
        msg += "大战：" + res["data"]["war"] + "\n"
        msg += "战场：" + res["data"]["battle"] + "\n"
        msg += "矿车：" + res["data"]["camp"] + "\n"
        msg += "驰援：" + res["data"]["relief"] + "\n"
        if "draw" in res["data"]:
            msg += "画画：" + res["data"]["draw"] + "\n"
        msg += "世界公共：" + res["data"]["team"][0] + "\n"
        msg += "五人本：" + res["data"]["team"][1] + "\n"
        msg += "十人本：" + res["data"]["team"][2]
        await daily.send(Message(msg))
    else:
        await daily.send(Message("查询失败"))


# 金价查询
@gold.handle()
async def gold_handle(event: MessageEvent, args: str = RegexMatched()):
    # 获取参数
    args = args.split()
    if len(args) == 1:
        server = jx3_config.server
    else:
        server = args[1]
    # 获取当前文件路径
    path = os.path.dirname(os.path.abspath(__file__))
    # 判断文件是否存在
    path += "/images/gold/" + server + datetime.datetime.now().strftime("%Y-%m-%d") + ".png"
    if not os.path.exists(path):

        res = request("/app/demon", {"server": server})
        data = res["data"]
        # 对data数据重新排序，按照时间排序
        data.sort(key=lambda x: x["date"])
        date = []
        value = {
            "wan_bao_lou": {
                "label": "万宝楼",
                "data": [],
            },
            "tie_ba": {
                "label": "贴吧",
                "data": [],
            },
            "other_1": {
                "label": "其他平台1",
                "data": [],
            },
            "other_2": {
                "label": "其他平台2",
                "data": [],
            },
        }
        for v in data:
            date.append(v["date"])
            wan_bao_lou_value = int(float(v["wanbaolou"]))
            tie_ba_value = int(float(v["tieba"]))
            other_1_value = int(float(v["dd373"]))
            other_2_value = int(float(v["uu898"]))
            value["wan_bao_lou"]["data"].append(wan_bao_lou_value)
            value["tie_ba"]["data"].append(tie_ba_value)
            value["other_1"]["data"].append(other_1_value)
            value["other_2"]["data"].append(other_2_value)
            # 画点
            plt.text(v["date"], wan_bao_lou_value, wan_bao_lou_value, ha="center", va="bottom", fontsize=10)
            plt.text(v["date"], tie_ba_value, tie_ba_value, ha="center", va="bottom", fontsize=10)
            plt.text(v["date"], other_1_value, other_1_value, ha="center", va="bottom", fontsize=10)
            plt.text(v["date"], other_2_value, other_2_value, ha="center", va="bottom", fontsize=10)
        # 画线
        minValue = None
        maxValue = None
        for k, v in value.items():
            # 计算v["data"]的平均数
            avg = sum(v["data"]) / len(v["data"])
            label = f"{v['label']}，均价：{avg:.0f}"
            plt.plot(date, v["data"], label=label)
            # 计算最大值和最小值
            if minValue is None:
                minValue = min(v["data"])
            elif minValue > min(v["data"]):
                minValue = min(v["data"])
            if maxValue is None:
                maxValue = max(v["data"])
            elif maxValue < max(v["data"]):
                maxValue = max(v["data"])

        # 图例右上角显示
        plt.legend(loc="upper right", prop=font)
        plt.title("【" + server + "】" + "金价", fontsize=20, fontproperties=font)
        plt.xticks(rotation=90, fontsize=14, fontproperties=font)
        plt.xlabel("日期", fontsize=12, fontproperties=font)
        plt.ylabel("价格", fontsize=18, fontproperties=font)
        plt.tick_params(axis='both', labelsize=10)
        plt.axis([date[0], date[-1], minValue, maxValue + (maxValue - minValue) * 0.5])
        # 保存为图片
        plt.savefig(path, bbox_inches='tight')
        plt.close()
    # 发送图片
    print(MessageSegment.image("file:///" + path))
    await daily.send(Message(MessageSegment.image("file:///" + path)))


# 小药查询
@medicine.handle()
async def medicine_handle(event: MessageEvent, args: str = RegexMatched()):
    # 获取参数
    args = args.split()
    if len(args) == 1:
        res = request("/app/heighten", {})
        if res["code"] == 200:
            await medicine.send(Message(MessageSegment.image(res["data"]["url"])))
            return
    name = args[1]
    name = jx3_profession_config.get_profession(jx3_profession_config, name)
    if name is None:
        await medicine.send(Message("心法不存在"))
    res = request("/app/heighten", {"name": name})
    if res["code"] == 200:
        if "name" not in res["data"] or res["data"]["name"] != name:
            await medicine.send(Message("心法不存在"))
        else:
            await medicine.send(Message(MessageSegment.image(res["data"]["url"])))
    else:
        await medicine.send(Message(res["msg"]))


# 宏查询
@macro.handle()
async def macro_handle(event: MessageEvent, args: str = RegexMatched()):
    # 获取参数
    args = args.split()
    name = args[1]
    name = jx3_profession_config.get_profession(jx3_profession_config, name)
    res = request("/app/macro", {"name": name})
    if res["code"] == 200:
        if "name" not in res["data"] or res["data"]["name"] != name:
            await macro.send(Message("宏不存在"))
        else:
            msg = "宏 【" + res["data"]["name"] + "】：\n"
            msg += res["data"]["macro"] + "\n"
            # 分割线
            msg += "奇穴" + "\n"
            qi_xue = res["data"]["qixue"].split(",")
            for v in qi_xue:
                msg += "[" + v + "]"
            msg += "\n仅作参考"
            await macro.send(Message(msg))
    else:
        await macro.send(Message(res["msg"]))


# 配装查询
@equip.handle()
async def equip_handle(event: MessageEvent, args: str = RegexMatched()):
    # 获取参数
    args = args.split()
    name = args[1]
    name = jx3_profession_config.get_profession(jx3_profession_config, name)
    res = request("/app/equip", {"name": name})
    if res["code"] == 200:
        if "name" not in res["data"] or res["data"]["name"] != name:
            await equip.send(Message("配装不存在"))
        else:
            await equip.send(Message(MessageSegment.image(res["data"]["pve"])))
    else:
        await equip.send(Message(res["msg"]))


# 骚话
@random.handle()
async def random_handle():
    res = request("/app/random", {})
    if res["code"] == 200:
        await random.send(Message(res["data"]["text"]))
