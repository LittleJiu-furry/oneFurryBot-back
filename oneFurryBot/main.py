from client import *
from msgbind import MsgBind
import ex
import asyncio
import opType
import os
import random
import platform

_about_me = {
    "name": "oneFurryBot",
    "dec":"",
    "author":"狐小九Little_Jiu",
    "version":"0.1-dev",
}

event = TypeBind() # 事件监听注册器
mBind = MsgBind() # 针对于消息内容进行相应的注册器

# 用于处理文件路径
def getPath(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))


# ============事件监听函数============

# 收到好友消息
@event.bind(opType.FriendMsg)
async def friend_message(_data:dict):
    data = FriendMessage(_data)
    await mBind.friend_call(data)

# 收到群消息
@event.bind(opType.GroupMsg)
async def group_message(_data:dict):
    data = GroupMessage(_data)
    await mBind.group_call(data)









# ===========功能函数================

ALLOW_NEXT = True
DISALLOW_NEXT = False

# 功能函数

# 签到功能
@mBind.Group_text("sign","签到")
async def sign(data:GroupMessage)->bool:
    # 判断当前群是否开启了全局签到
    enable = False
    conf = {}
    try:
        with open(getPath("./config/Gconf.json"), mode="r+",encoding="utf-8") as f:
            f.seek(0,0)
            conf = json.load(f)
            try:
                enable = conf[f"G{str(data.fromGroup)}"]["enable"]
            except KeyError:
                # 一旦触发KeyError,就说明配置文件里面不存在这个配置项
                # 为配置文件补写此配置项,此项默认关闭
                conf[f"G{str(data.fromGroup)}"] = {"enable": False}
                enable = False
                f.seek(0,0)
                f.truncate(0)
                f.write(json.dumps(conf))
    except FileNotFoundError:
        # 配置文件不存在
        with open(getPath("./config/Gconf.json"), mode="a+",encoding="utf-8") as f:
            conf = {}
            conf[f"G{str(data.fromGroup)}"] = {"enable": False}
            enable = False
            f.write(json.dumps(conf))
    if(enable):
        # 开启了
        _valueRange = botConfig["signBot"]["signValueRange"]
        _value = random.randint(_valueRange[0],_valueRange[1])
        date = time.localtime(data.msgChain.getSource().msgTime)
        try:
            with open(getPath("./config/sign.json"), mode="r+",encoding="utf-8") as f:
                signData = json.load(f)
                try:
                    _userData = signData[f"U{str(data.fromQQ)}"]
                    lastSignData = time.localtime(_userData["lastSignTimestamp"])
                    if(date.tm_yday == lastSignData.tm_yday):
                        # 今天已经签到了
                        msg = MsgChain()
                        msg.addAt(data.fromQQ)
                        for _text in botConfig["signBot"]["signText_faile"]:
                            _text = str(_text).replace("{{ GroupName }}",str(_userData["lastSignGroup_name"]))
                            _text = str(_text).replace("{{ GroupId }}",str(_userData["lastSignGroup"]))
                            msg.addTextMsg(_text)
                        await bot.sendGroupMsg(msg,data.fromGroup)
                    elif(date.tm_yday > lastSignData.tm_yday or (date.tm_yday == 1 and lastSignData.tm_yday > date.tm_yday and date.tm_year > lastSignData.tm_year)):
                        # 今天的年日期大于上次签到的年日期
                        # 或者今天的年日期为1，上次签到的年日期比当前年日期大，并且上次签到的年份小于当前年份
                        # 今天还没有签到
                        _userData["lastSignGroup"] = data.fromGroup
                        _userData["lastSignGroup_name"] = data.fromGroup_name
                        _userData["lastSignTimestamp"] = data.msgChain.getSource().msgTime
                        _userData["signValue"] += _value
                        _userData["signDate"]["thisMonth"].append(date.tm_mday)
                        signData[f"U{str(data.fromQQ)}"] = _userData
                        f.seek(0,0)
                        f.truncate(0)
                        f.write(json.dumps(signData,ensure_ascii=False))
                        msg = MsgChain()
                        msg.addAt(data.fromQQ)
                        for _text in botConfig["signBot"]["signText"]:
                            _text = str(_text).replace("{{ newValue }}",str(_value))
                            _text = str(_text).replace("{{ signName }}",str(botConfig["signBot"]["signName"]))
                            _text = str(_text).replace("{{ totalValue }}",str(_userData["signValue"]))
                            msg.addTextMsg(_text)
                        await bot.sendGroupMsg(msg,data.fromGroup)
                except KeyError:
                    # 一旦触发KeyError,就说明配置文件里面不存在这个配置项
                    signData[f"U{str(data.fromQQ)}"] = {
                        "lastSignGroup": data.fromGroup,
                        "lastSignGroup_name":data.fromGroup_name, 
                        "lastSignTimestamp": data.msgChain.getSource().msgTime,
                        "signValue": _value,
                        "signDate":{
                            "thisMonth":[date.tm_mday]
                        }
                    }
                    f.seek(0,0)
                    f.truncate(0)
                    f.write(json.dumps(signData))
                    msg = MsgChain()
                    msg.addAt(data.fromQQ)
                    for _text in botConfig["signBot"]["signText"]:
                            _text = str(_text).replace("{{ newValue }}",str(_value))
                            _text = str(_text).replace("{{ signName }}",str(botConfig["signBot"]["signName"]))
                            _text = str(_text).replace("{{ totalValue }}",str(signData[f"U{str(data.fromQQ)}"]["signValue"]))
                            msg.addTextMsg(_text)
                    await bot.sendGroupMsg(msg,data.fromGroup)
        except FileNotFoundError:
            with open(getPath("./config/sign.json"), mode="a+",encoding="utf-8") as f:
                # 没有这个文件
                # 说明还没有任何人签到过
                uconf = {                    
                    f"U{data.fromQQ}":{
                        "lastSignGroup": data.fromGroup,
                        "lastSignGroup_name":data.fromGroup_name, 
                        "lastSignTimestamp": data.msgChain.getSource().msgTime,
                        "signValue": _value,
                        "signDate":{
                            "thisMonth":[date.tm_mday]
                        }
                    }
                }
                f.write(json.dumps(uconf))
                msg = MsgChain()
                msg.addAt(data.fromQQ)
                for _text in botConfig["signBot"]["signText"]:
                    _text = str(_text).replace("{{ newValue }}",str(_value))
                    _text = str(_text).replace("{{ signName }}",str(botConfig["signBot"]["signName"]))
                    _text = str(_text).replace("{{ totalValue }}",str(uconf[f"U{str(data.fromQQ)}"]["signValue"]))
                    msg.addTextMsg(_text)

                await bot.sendGroupMsg(msg,data.fromGroup)
    return ALLOW_NEXT

# 菜单
@mBind.Group_text("#菜单","#menu")
async def menu(data:GroupMessage)->bool:
    msg = MsgChain()
    msg.addTextMsg("=OneFurryBot=")
    msg.addTextMsg("#菜单 #menu 打开菜单")
    msg.addTextMsg("#系统信息 #system 查看系统信息")
    msg.addTextMsg("")
    msg.addTextMsg("机器人正在开发中，更多功能即将来临")
    msg.addTextMsg("=By LittleJiu=")
    await bot.sendGroupMsg(msg,data.fromGroup)
    return ALLOW_NEXT
    
# 系统信息 
@mBind.Group_text("#系统信息","#system")
@mBind.Friend_text("#系统信息","#system")
async def systemInfo(data)->bool:
    msg = MsgChain()
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg("所用框架: Mirai")
    msg.addTextMsg(f'当前插件版本: {_about_me["version"]}')
    msg.addTextMsg(f'当前平台: {platform.system()}')
    msg.addTextMsg(f'平台版本信息: {platform.version()}')
    msg.addTextMsg(f'当前Python版本: {platform.python_version()}')
    _now = time.localtime(time.time())
    msg.addTextMsg(f'当前系统时间: {time.strftime("%Y-%m-%d %H:%M:%S", _now)}')
    msg.addTextMsg("-=By LittleJiu=-")
    if(type(data) == GroupMessage):
        # 来自群里
        await bot.sendGroupMsg(msg,data.fromGroup)
    elif(type(data) == FriendMessage and data.fromQQ == botConfig["owner"]):
        # 来自好友
        await bot.sendFriendMsg(msg,data.fromQQ)
    return ALLOW_NEXT

# 关闭
@mBind.Group_text("#关闭","#close")
@mBind.Friend_text("#关闭","#close")
async def closeFunc(data)->bool:
    if(data.fromQQ == botConfig["owner"]):
        msg = MsgChain()
        msg.addTextMsg("已关闭")
        if(type(data) == GroupMessage):
            # 来自群里
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage and data.fromQQ == botConfig["owner"]):
            # 来自好友
            await bot.sendFriendMsg(msg,data.fromQQ)
        bot.close()
    return ALLOW_NEXT


# 重载配置
@mBind.Group_text("#重载配置","#reload")
@mBind.Friend_text("#重载配置","#reload")
async def reloadFunc(data)->bool:
    if(data.fromQQ == botConfig["owner"]):
        msg = MsgChain()
        msg.addTextMsg("正在重载配置...")
        if(type(data) == GroupMessage):
            # 来自群里
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage and data.fromQQ == botConfig["owner"]):
            # 来自好友
            await bot.sendFriendMsg(msg,data.fromQQ)
        main()
        msg.clearMsgChain()
        msg.addTextMsg("配置重载成功")
        if(type(data) == GroupMessage):
            # 来自群里
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage and data.fromQQ == botConfig["owner"]):
            # 来自好友
            await bot.sendFriendMsg(msg,data.fromQQ)
    return ALLOW_NEXT






# ======程序入口======

# 读取配置
def main():
    # 读取机器人账号配置
    with open(getPath("./config/bot.json"),mode="r",encoding="utf-8") as f:
        botAccount = json.load(f)
    # 将配置读入内存
    try:
        with open(getPath("./config/conf.json"),encoding="utf-8",mode="r+") as f:
            botConfig = json.load(f)
    except FileNotFoundError:
        # 文件不存在,将进行创建
        with open(getPath("./config/conf.json"),encoding="utf-8",mode="a+") as f:
            botConfig["signBot"] = {}
            botConfig["signBot"]["signValueRange"] = [10,100]
            botConfig["signBot"]["signTimeRange"] = [0,0]
            botConfig["signBot"]["signName"] = "积分"
            botConfig["signText"] = [
                "签到成功",
                "本次签到获得 {{ newValue }} 点{{ signName }}",
                "当前有 {{ totalValue }} 点{{ signName }}"
            ]
            botConfig["signText"]["signText_faile"] = [
                "你今天已经在 {{ GroupName }}({{ GroupId }})签到过了，请不要重复签到~"
            ]
            botConfig["ui"] = {}
            botConfig["ui"]["port"] = 9000
            botConfig["owner"] = 2638239785
            f.write(json.dumps(botConfig))
    


# 入口
if __name__ == "__main__":
    botAccount = {}
    botConfig = {}
    main()
    bot = Bot(botAccount["vk"],botAccount["account"],event,botAccount["baseURL"])
    bot.connect()
