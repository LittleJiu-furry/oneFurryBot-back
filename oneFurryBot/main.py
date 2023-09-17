from client import *
from msgbind import MsgBind
import asyncio
import opType
import random
import platform
import io
import base64
import ex

_about_me = {
    "name": "oneFurryBot",
    "dec":"",
    "author":"狐小九Little_Jiu",
    "version":"0.2-dev",
}

botAccount = {}
botConfig = {}

event = TypeBind() # 事件监听注册器
mBind = MsgBind() # 针对于消息内容进行相应的注册器




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
        with open(ex.getPath("./config/Gconf.json"), mode="r+",encoding="utf-8") as f:
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
        with open(ex.getPath("./config/Gconf.json"), mode="a+",encoding="utf-8") as f:
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
            with open(ex.getPath("./config/sign.json"), mode="r+",encoding="utf-8") as f:
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
                        if(date.tm_mon != lastSignData.tm_mon):
                            _userData["signDate"]["thisMonth"] = [date.tm_mday]
                        else:
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
            with open(ex.getPath("./config/sign.json"), mode="a+",encoding="utf-8") as f:
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
    msg.addTextMsg("#我的信息 #me 获得你的一些信息")
    msg.addTextMsg("#补签 [日期] 进行补签，每次补签扣除30分")
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

        msg.clearMsgChain()
        msg.addTextMsg("配置重载成功")
        if(type(data) == GroupMessage):
            # 来自群里
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage and data.fromQQ == botConfig["owner"]):
            # 来自好友
            await bot.sendFriendMsg(msg,data.fromQQ)
    return ALLOW_NEXT

# 获取信息
@mBind.Group_text("#我的信息","#me")
@mBind.Friend_text("#我的信息","#me")
async def getMe(data)->bool:
    msg = MsgChain()
    try:
        with open(ex.getPath("./config/sign.json"),mode="r",encoding="utf-8") as f:
            userData = json.load(f)
        try:
            userData = userData[f"U{data.fromQQ}"]
            if(type(data) == GroupMessage):
                # 来自群里
                msg.addAt(data.fromQQ)
            msg.addTextMsg(f'总积分: {userData["signValue"]}')
            msg.addTextMsg(f'最后一次签到在 {userData["lastSignGroup_name"]}({userData["lastSignGroup"]})')
            msg.addTextMsg(f'签到时间: {time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(userData["lastSignTimestamp"]))}')

            import calendar as cal
            from PIL import Image, ImageDraw, ImageFont

            now = time.localtime(time.time())
            cal.setfirstweekday(6)
            monthStr = cal.month(now.tm_year,now.tm_mon)
            signedDay = userData["signDate"]["thisMonth"]
            # 对文字进行处理
            monthStrList = monthStr.split("\n")
            imageList = []
            firstLine = True
            font = ImageFont.truetype(ex.getPath("./imgFont.ttf"),25)
            for raw in monthStrList[1:]:
                _indexList = []
                for index in range(0,len(raw),3):
                    word = raw[index:index+2]
                    baseSize = (40,40)
                    if(firstLine):
                        backColor = (255,255,255)
                    else:
                        if(word != "  " and int(word) in signedDay):
                            backColor = (0,255,0)
                        else:
                            backColor = (255,255,255)
                    word = word.replace(" ","") # 删除其中的空格
                    _img = Image.new("RGB", baseSize, backColor)
                    _dr = ImageDraw.Draw(_img)
                    x1,y1,x2,y2 = _dr.textbbox((0,0),word,font=font)
                    _dr.text(((baseSize[0]-x2)/2,(baseSize[1]-y2)/2),word,font=font, fill=(0, 0, 0))
                    _indexList.append(_img)
                firstLine = False
                if(len(_indexList) != 0):
                    imageList.append(_indexList)
                await asyncio.sleep(0)
            # 构造标题
            title = monthStrList[0]
            _title = Image.new("RGB", (280,40), (255, 255, 255))
            _dr = ImageDraw.Draw(_title)
            x1,y1,x2,y2 = _dr.textbbox((0,0),title,font=font)
            _dr.text(((280-x2)/2,(40-y2)/2),title,font=font, fill=(0, 0, 0))
            image = Image.new("RGB", (280,(len(imageList) + 1)* 40), (255, 255, 255))
            dr = ImageDraw.Draw(image)
            image.paste(_title, (0,0))
            for rawImageListIndex in range(len(imageList)):
                for imgIndex in range(len(imageList[rawImageListIndex])):
                    img = imageList[rawImageListIndex][imgIndex]
                    image.paste(img, (40 * imgIndex,40 * (rawImageListIndex + 1)))
                    await asyncio.sleep(0)
                await asyncio.sleep(0)
            ioBytes = io.BytesIO()
            image.save(ioBytes,format="png")
            imgBase64 = base64.b64encode(ioBytes.getvalue()).decode()
            msg.addTextMsg("签到日历")
            msg.addImg_Base64(imgBase64)

        except KeyError:
            if(type(data) == GroupMessage):
                # 来自群里
                msg.addAt(data.fromQQ)
                msg.addTextMsg("你的数据有误，暂时无法读取，如果多次遇到此问题，请提交反馈")
    except FileNotFoundError:
        if(type(data) == GroupMessage):
            # 来自群里
            msg.addAt(data.fromQQ)
    if(type(data) == GroupMessage):
        # 来自群里
        await bot.sendGroupMsg(msg,data.fromGroup)
    elif(type(data) == FriendMessage):
        # 来自好友
        await bot.sendFriendMsg(msg,data.fromQQ)
    return ALLOW_NEXT
  

    msg = MsgChain()
    msg.addTextMsg(f'获得参数 arg: {kwargs["arg"]}')
    await bot.sendGroupMsg(msg,data.fromGroup)
    return ALLOW_NEXT

# 补签功能
@mBind.Group_text("#补签 {day}","#补签")
@mBind.Friend_text("#补签 {day}","#补签")
async def signDay(data,args:dict = None):
    msg = MsgChain()
    if(args == None):
        # 没有指定日期
        if(type(data) == GroupMessage):
            msg.addAt(data.fromQQ)
            msg.addTextMsg("请指定日期")
            msg.addTextMsg("格式为 #补签 {日期}")
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage):
            msg.addTextMsg("请指定日期")
            msg.addTextMsg("格式为 #补签 {日期}")
            await bot.sendFriendMsg(msg,data.fromQQ)
        return ALLOW_NEXT
    else:
        _day = int(args["day"])
        # 获得本月日期的最大值
        import calendar as cal
        _now = time.localtime(time.time())
        _firstWeekDay,_maxDay = cal.monthrange(_now.tm_year,_now.tm_mon)
        if(1 <= _day <= _maxDay and 1 <= _day < _now.tm_mday):
            userData = ex.getUserData(data.fromQQ)
            if(_day in userData.thisMonth):
                # 已经签过
                if(type(data) == GroupMessage):
                    msg.addAt(data.fromQQ)
                msg.addTextMsg("当天已签到，不允许补签")
                if(type(data) == GroupMessage):
                    await bot.sendGroupMsg(msg,data.fromGroup)
                elif(type(data) == FriendMessage):
                    await bot.sendFriendMsg(msg,data.fromQQ)
                return ALLOW_NEXT
            userData.thisMonth.append(_day)
            userData.signValue -= botConfig["signBot"]["reSignCutValue"]
            valueRange = botConfig["signBot"]["signValueRange"]
            _value = random.randint(valueRange[0],valueRange[1])
            userData.signValue += _value
            ex.writeUserData(userData,data.fromQQ)
            if(type(data) == GroupMessage):
                msg.addAt(data.fromQQ)
                msg.addTextMsg("补签成功")
                msg.addTextMsg(f'补签已经扣除{botConfig["signBot"]["reSignCutValue"]}点{botConfig["signBot"]["signName"]}')
                msg.addTextMsg(f'补签获得了{_value}点{botConfig["signBot"]["signName"]}')
                await bot.sendGroupMsg(msg,data.fromGroup)
            elif(type(data) == FriendMessage):
                msg.addTextMsg("补签成功")
                msg.addTextMsg(f'补签已经扣除{botConfig["signBot"]["reSignCutValue"]}点{botConfig["signBot"]["signName"]}')
                msg.addTextMsg(f'补签获得了{_value}点{botConfig["signBot"]["signName"]}')
                await bot.sendFriendMsg(msg,data.fromQQ)
        else:
            if(type(data) == GroupMessage):
                msg.addAt(data.fromQQ)
            
            msg.addTextMsg("补签失败")
            msg.addTextMsg("仅允许在本月份已经过但未签到的日期补签")

            if(type(data) == GroupMessage):
                await bot.sendGroupMsg(msg,data.fromGroup)
            elif(type(data) == FriendMessage):
                await bot.sendFriendMsg(msg,data.fromQQ)
    return ALLOW_NEXT

# 开关设置
@mBind.Group_text("#开启","#enable")
@mBind.Friend_text("#开启 {group}","#enable {group}")
async def enableGroup(data,args:dict = None):
    msg = MsgChain()
    if(data.fromQQ == botConfig["owner"]):
        # 确保是主人在操作
        if(args == None):
            # 指令来自群
            msg.addAt(data.fromQQ)
            group = data.fromGroup
        else:
            group = args["group"]
        
        try:
            with open(ex.getPath("./config/Gconf.json"),mode="r+",encoding="utf-8") as f:
                _conf = json.load(f)
                try:
                    nowStatus = _conf[f'G{group}']["enable"]
                    if(nowStatus):
                        msg.addTextMsg("当前群已开启,请不要重复开启")
                    else:
                        in_data = {f'G{group}':{"enable":True}}
                        _conf.update(in_data)
                        f.seek(0,0)
                        f.truncate(0)
                        f.write(json.dumps(_conf,indent=4,ensure_ascii=False))
                        msg.addTextMsg("已开启")
                except KeyError:
                    # 说明配置文件中不存在当前需求的配置项
                    in_data = {f'G{group}':{"enable":True}}
                    _conf.update(in_data)
                    f.seek(0,0)
                    f.truncate(0)
                    f.write(json.dumps(_conf,indent=4,ensure_ascii=False))
                    msg.addTextMsg("已开启")
        except FileNotFoundError:
            with open(ex.getPath("./config/Gconf.json"),mode="a+",encoding="utf-8") as f:
                new_data = {f'G{group}':{"enable":True}}
                msg.addTextMsg("已开启")
                f.write(json.dumps(new_data,indent=4,ensure_ascii=False))

        if(type(data) == GroupMessage):
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage):
            await bot.sendFriendMsg(msg,data.fromQQ)
    return ALLOW_NEXT









# ======程序入口======

# 读取配置
def main():
    global botAccount,botConfig
    # 读取机器人账号配置
    with open(ex.getPath("./config/bot.json"),mode="r",encoding="utf-8") as f:
        botAccount = json.load(f)
    # 将配置读入内存,读取botConfig
    try:
        with open(ex.getPath("./config/conf.json"),encoding="utf-8",mode="r+") as f:
            botConfig = json.load(f)
    except FileNotFoundError:
        # 文件不存在,将进行创建
        with open(ex.getPath("./config/conf.json"),encoding="utf-8",mode="a+") as f:
            botConfig["signBot"] = {}
            botConfig["signBot"]["signValueRange"] = [10,100]
            botConfig["signBot"]["signTimeRange"] = [0,0]
            botConfig["signBot"]["signName"] = "积分"
            botConfig["signBot"]["signText"] = [
                "签到成功",
                "本次签到获得 {{ newValue }} 点{{ signName }}",
                "当前有 {{ totalValue }} 点{{ signName }}"
            ]
            botConfig["signBot"]["signText_faile"] = [
                "你今天已经在 {{ GroupName }}({{ GroupId }})签到过了，请不要重复签到~"
            ]
            botConfig["signBot"]["reSignCutValue"] = 30
            botConfig["ui"] = {}
            botConfig["ui"]["port"] = 9000
            botConfig["owner"] = 2638239785
            f.write(json.dumps(botConfig))
            


# 入口
if __name__ == "__main__":
    main()
    bot = Bot(botAccount["vk"],botAccount["account"],event,botAccount["baseURL"])
    bot.connect()
