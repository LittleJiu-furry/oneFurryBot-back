from client import *
from msgbind import MsgBind
import ex
import asyncio
import opType
import os
import random

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
@mBind.Group_text("sign","签到")
async def sign(data:GroupMessage)->bool:
    # 判断当前群是否开启了全局签到
    enable = False
    conf = {}
    try:
        with open(getPath("./config/conf.json"), mode="r+",encoding="utf-8") as f:
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
        with open(getPath("./config/conf.json"), mode="a+",encoding="utf-8") as f:
            conf = {}
            conf[f"G{str(data.fromGroup)}"] = {"enable": False}
            enable = False
            f.write(json.dumps(conf))
    if(enable):
        # 开启了
        _value = random.randint(10,100)
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
                        msg.addTextMsg(f'你今天已经在{str(_userData["lastSignGroup"])}签到过了，不可以重复签到哦~')
                        await bot.sendGroupMsg(msg,data.fromGroup)
                    elif(date.tm_yday > lastSignData.tm_yday):
                        # 今天还没有签到
                        _userData["lastSignGroup"] = data.fromGroup
                        _userData["lastSignTimestamp"] = data.msgChain.getSource().msgTime
                        _userData["signValue"] += _value
                        _userData["signDate"]["thisMonth"].append(date.tm_mday)
                        signData[f"U{str(data.fromQQ)}"] = _userData
                        f.seek(0,0)
                        f.truncate(0)
                        f.write(json.dumps(signData))
                        msg = MsgChain()
                        msg.addAt(data.fromQQ)
                        msg.addTextMsg(f'签到成功喵~\n')
                        msg.addTextMsg(f'获得了{str(_value)}点积分\n')
                        msg.addTextMsg(f'当前有{str(_userData["signValue"])}点积分\n')
                        await bot.sendGroupMsg(msg,data.fromGroup)
                except KeyError:
                    # 一旦触发KeyError,就说明配置文件里面不存在这个配置项
                    signData[f"U{str(data.fromQQ)}"] = {
                        "lastSignGroup": data.fromGroup, 
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
                    msg.addTextMsg(f'签到成功喵~\n')
                    msg.addTextMsg(f'获得了{str(_value)}点积分\n')
                    _value = str(signData[f"U{str(data.fromQQ)}"]["signValue"])
                    msg.addTextMsg(f'当前有{_value}点积分\n')
                    await bot.sendGroupMsg(msg,data.fromGroup)
        except FileNotFoundError:
            with open(getPath("./config/sign.json"), mode="a+",encoding="utf-8") as f:
                # 没有这个文件
                # 说明还没有任何人签到过
                uconf = {                    
                    f"U{data.fromQQ}":{
                        "lastSignGroup": data.fromGroup, 
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
                msg.addTextMsg(f'签到成功喵~\n')
                msg.addTextMsg(f'获得了{str(_value)}点积分\n')
                _value = str(uconf[f'U{data.fromQQ}']["signValue"])
                msg.addTextMsg(f'当前有{_value}点积分\n')
                await bot.sendGroupMsg(msg,data.fromGroup)
    return ALLOW_NEXT


    
    


    





# 入口
if __name__ == "__main__":
    bot = Bot("Abyss-Reg031204",3235302005,event)
    bot.connect()
