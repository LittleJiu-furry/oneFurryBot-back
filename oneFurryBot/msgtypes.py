import asyncio
import time
import base64 as b64

# 消息链-来源
class MsgChainSource:
    msgTime = 0
    msgId = 0
    def __init__(self,inSorce:dict) -> None:
        self.msgTime = inSorce["time"]
        self.msgId = inSorce["id"]

# 单独处理消息链
class MsgChain:
    def __init__(self,inChain:list = None):
        self.msgChain = ([] if inChain is None else inChain)
    def addTextMsg(self,content:str):
        self.msgChain.append({"type":"Plain","text":content})
    def addImg(self,imgPath:str):
        with open(imgPath,"rb") as f:
            img = f.read()
            img = b64.b64encode(img)
            imgBase64 = img.decode()
        self.msgChain.append({"type":"Image","base64":imgBase64})
    def addAt(self,qq:int,space:bool = True):
        self.msgChain.append({"type":"At","target":qq,"display":""})
        if(space):
            # 为at添加空格
            self.addTextMsg(" ")


    async def getTextMsg(self):
        _msg = ""
        for msg in self.msgChain:
            if msg["type"] == "Plain":
                _msg += msg["text"]
            await asyncio.sleep(0)
        return _msg
    
    async def getImgs(self):
        _imgs = []
        for msg in self.msgChain:
            if msg["type"] == "Image":
                _imgs.append(msg["url"])
            await asyncio.sleep(0)
        return _imgs

    async def getQuote(self):
        _quote = {}
        for msg in self.msgChain:
            if msg["type"] == "Quote":
                tempD = {
                    "id": msg["id"],
                    "groupId": msg["groupId"],
                    "senderId": msg["senderId"],
                    "targetId": msg["targetId"],
                    "origin": msg["origin"]
                }
                _quote = tempD
                break
            await asyncio.sleep(0)
        return _quote
    def getSource(self) -> MsgChainSource:
        msg = self.msgChain[0]
        if msg["type"] == "Source":
            return MsgChainSource(msg)
            

# 好友消息
class FriendMessage:
    fromQQ = 0
    nickName = ""
    remark = ""
    msgChain = None
    def __init__(self, message:dict):
        msg = message
        self.fromQQ = msg["sender"]["id"]
        self.nickName = msg["sender"]["nickname"]
        self.remark = msg["sender"]["remark"]
        self.msgChain = MsgChain(msg["messageChain"])

# 群消息
class GroupMessage:
    fromQQ = 0
    fromQQ_name = ""
    fromQQ_specialTitle = ""
    fromQQ_joinTimeStamp = 0
    fromQQ_lastSpeakTimeStamp = 0
    fromQQ_muteTimeRemaining = 0
    fromQQ_permission = ""
    fromGroup = 0
    fromGroup_name = ""
    fromGroup_botPermission = ""
    msgChain = None
    def __init__(self,message:dict) -> None:
        self.fromQQ = message["sender"]["id"]
        self.fromGroup = message["sender"]["group"]["id"]
        self.fromQQ_name = message["sender"]["memberName"]
        self.fromQQ_specialTitle = message["sender"]["specialTitle"]
        self.fromQQ_joinTimeStamp = message["sender"]["joinTimestamp"]
        self.fromQQ_lastSpeakTimeStamp = message["sender"]["lastSpeakTimestamp"]
        self.fromQQ_muteTimeRemaining = message["sender"]["muteTimeRemaining"]
        self.fromQQ_permission = message["sender"]["permission"]
        self.fromGroup_name = message["sender"]["group"]["name"]
        self.fromGroup_botPermission = message["sender"]["group"]["permission"]
        self.msgChain = MsgChain(message["messageChain"])

    
