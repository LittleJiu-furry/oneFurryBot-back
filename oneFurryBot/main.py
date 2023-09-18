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
    "version":"0.3-dev",
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


# =======签到机器人============

# 签到功能
@mBind.Group_text("sign","签到")
async def sign(data:GroupMessage)->bool:
    msg = MsgChain()
    msg.addAt(data.fromQQ)
    # 判断是否开启
    enable = ex.getGroupEnable(data.fromGroup,"signBot")
    if(enable):
        userData = ex.getUserSignData(data.fromQQ)
        # 判断今天是否已经签到
        _last = time.localtime(userData.lastSignTimestamp)
        _now = time.localtime(data.msgChain.getSource().msgTime)

        if(_last.tm_yday == _now.tm_yday):
            # 今天已经签到
            for text in botConfig.signConfig.signText_faile:
                text = text.replace("{{ GroupName }}",f"{userData.lastSignGroup_name}")
                text = text.replace("{{ GroupId }}",f"{userData.lastSignGroup}")
                msg.addTextMsg(text)
            await bot.sendGroupMsg(msg,data.fromGroup)
        else:
            # 今天未签到
            # 需要判断是否在签到时间段内，并清理签到日历
            minH,maxH = botConfig.signConfig.signTimeRange
            # 构造时间戳范围
            _min = time.mktime(time.strptime(f'{_now.tm_year}-{_now.tm_mon}-{_now.tm_mday} {minH}:00:00',"%Y-%m-%d %H:%M:%S"))
            _max = time.mktime(time.strptime(f'{_now.tm_year}-{_now.tm_mon}-{_now.tm_mday} {maxH}:59:59',"%Y-%m-%d %H:%M:%S"))
            _nt = time.mktime(_now)
            if(_min <= _nt <= _max):
                # 在签到时间段内
                valueMin,valueMax = botConfig.signConfig.signValueRange
                _value = random.randint(valueMin,valueMax)
                userData.signValue += _value
                userData.lastSignTimestamp = data.msgChain.getSource().msgTime
                userData.lastSignGroup = data.fromGroup
                userData.lastSignGroup_name = data.fromGroup_name
                # 更新签到日历
                if(_now.tm_mon != _last.tm_mon):
                    userData.thisMonth = [_now.tm_mday]
                else:
                    userData.thisMonth.append(_now.tm_mday)
                ex.writeUserData(userData,data.fromQQ)
                for text in botConfig.signConfig.signText:
                    text = text.replace("{{ newValue }}",f"{_value}")
                    text = text.replace("{{ signName }}",f"{botConfig.signConfig.signName}")
                    text = text.replace("{{ totalValue }}",f"{userData.signValue}")
                    msg.addTextMsg(text)
                await bot.sendGroupMsg(msg,data.fromGroup)
            else:
                # 不在签到时段
                msg.addTextMsg("不在签到时段")
                msg.addTextMsg(f"签到时段为{minH}:00:00 ~ {maxH}:59:59")
                await bot.sendGroupMsg(msg,data.fromGroup)
    return ALLOW_NEXT

# 补签功能
@mBind.Group_text("#补签 {day}","#补签")
@mBind.Friend_text("#补签 {day}","#补签")
async def signDay(data,day):
    msg = MsgChain()
    if(day == None):
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
        _day = int(day)
        # 获得本月日期的最大值
        import calendar as cal
        _now = time.localtime(time.time())
        _firstWeekDay,_maxDay = cal.monthrange(_now.tm_year,_now.tm_mon)
        if(1 <= _day <= _maxDay and 1 <= _day < _now.tm_mday):
            userData = ex.getUserSignData(data.fromQQ)
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
            userData.signValue -= botConfig.signConfig.reSignCutValue
            valueRange = botConfig.signConfig.signValueRange
            _value = random.randint(valueRange[0],valueRange[1])
            userData.signValue += _value
            ex.writeUserData(userData,data.fromQQ)
            if(type(data) == GroupMessage):
                msg.addAt(data.fromQQ)
                msg.addTextMsg("补签成功")
                msg.addTextMsg(f'补签已经扣除{botConfig.signConfig.reSignCutValue}点{botConfig.signConfig.signName}')
                msg.addTextMsg(f'补签获得了{_value}点{botConfig.signConfig.signName}')
                await bot.sendGroupMsg(msg,data.fromGroup)
            elif(type(data) == FriendMessage):
                msg.addTextMsg("补签成功")
                msg.addTextMsg(f'补签已经扣除{botConfig.signConfig.reSignCutValue}点{botConfig.signConfig.signName}')
                msg.addTextMsg(f'补签获得了{_value}点{botConfig.signConfig.signName}')
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


# ==========宠物系统============

# # 领养宠物
# @mBind.Group_text("#领养宠物","#pet")
# @mBind.Friend_text("#领养宠物","#pet")
# async def getNewPet(data,args):
#     # 创建一个新的宠物信息
#     ex.createPet(data.fromQQ)




# ==========杂项===========

# 菜单
@mBind.Group_text("#菜单","#menu")
async def menu(data:GroupMessage)->bool:
    msg = MsgChain()
    msg.addTextMsg("-=OneFurryBot=-")
    msg.addTextMsg("#菜单 #menu 打开菜单")
    msg.addTextMsg("#系统信息 #system 查看系统信息")
    msg.addTextMsg("#我的信息 #me 获得你的一些信息")
    msg.addTextMsg("#补签 [日期] 进行补签，每次补签扣除30分")
    msg.addTextMsg("")
    msg.addTextMsg("机器人正在开发中，更多功能即将来临")
    msg.addTextMsg("-=By LittleJiu=-")
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
    elif(type(data) == FriendMessage and data.fromQQ == botConfig.owner):
        # 来自好友
        await bot.sendFriendMsg(msg,data.fromQQ)
    return ALLOW_NEXT

# 关闭
@mBind.Group_text("#关闭","#close")
@mBind.Friend_text("#关闭","#close")
async def closeFunc(data)->bool:
    if(data.fromQQ == botConfig.owner):
        msg = MsgChain()
        msg.addTextMsg("已关闭")
        if(type(data) == GroupMessage):
            # 来自群里
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage and data.fromQQ == botConfig.owner):
            # 来自好友
            await bot.sendFriendMsg(msg,data.fromQQ)
        bot.close()
    return ALLOW_NEXT

# 重载配置
@mBind.Group_text("#重载配置","#reload")
@mBind.Friend_text("#重载配置","#reload")
async def reloadFunc(data)->bool:
    if(data.fromQQ == botConfig.owner):
        msg = MsgChain()
        msg.addTextMsg("正在重载配置...")
        if(type(data) == GroupMessage):
            # 来自群里
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage and data.fromQQ == botConfig.owner):
            # 来自好友
            await bot.sendFriendMsg(msg,data.fromQQ)
        main() # 重载配置
        msg.clearMsgChain()
        msg.addTextMsg("配置重载成功")
        if(type(data) == GroupMessage):
            # 来自群里
            await bot.sendGroupMsg(msg,data.fromGroup)
        elif(type(data) == FriendMessage and data.fromQQ == botConfig.owner):
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










# ======程序入口======

# 读取配置
def main():
    global botAccount,botConfig
    # 读取机器人账号配置
    with open(ex.getPath("./config/bot.json"),mode="r",encoding="utf-8") as f:
        botAccount = json.load(f)
    # 将配置读入内存,读取botConfig
    botConfig = ex.getRobotConf()
            


# 入口
if __name__ == "__main__":
    main()
    bot = Bot(botAccount["vk"],botAccount["account"],event,botAccount["baseURL"])
    bot.connect()
