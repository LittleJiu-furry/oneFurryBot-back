'''
    本模块提供一些已经封装好的方法函数，便于读取用户数据
'''
import os
import json

# =========数据结构定义=========

# 用户数据结构
class userDataClass:
    lastSignGroup = 0
    lastSignGroup_name = ""
    lastSignTimestamp = 0
    signValue = 0
    thisMonth = []
    def __init__(self,_data:dict == None) -> None:
        if(_data is not None and _data != {}):
            self.lastSignGroup =_data["lastSignGroup"]
            self.lastSignGroup_name = _data["lastSignGroup_name"]
            self.lastSignTimestamp = _data["lastSignTimestamp"]
            self.signValue = _data["signValue"]
            self.thisMonth = _data["signDate"]["thisMonth"]



# ===========方法函数===========

# 用于处理文件路径
def getPath(*path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), *path))

# 获得用户数据
def getUserData(user_id:str) -> userDataClass:
    try:
        with open(getPath("./config/sign.json"),mode="r",encoding="utf-8") as f:
            try:
                user_data = json.load(f)[f"U{user_id}"]
            except KeyError:
                return userDataClass()
    except FileNotFoundError:
        return userDataClass()
    
    return userDataClass(user_data)

# 覆写用户数据
def writeUserData(userDict:userDataClass,user_id:str):
    # 构造写入的数据
    new_data = {
        f"U{user_id}":{
            "lastSignGroup":userDict.lastSignGroup,
            "lastSignGroup_name":userDict.lastSignGroup_name,
            "lastSignTimestamp":userDict.lastSignTimestamp,
            "signValue":userDict.signValue,
            "signDate":{
                "thisMonth":userDict.thisMonth
            }
        }
    }
    try:
        with open(getPath("./config/sign.json"),mode="r+",encoding="utf-8") as f:
            _old = json.load(f) # 读取并暂存旧数据
            _new = _old.copy()
            _new.update(new_data)
            f.seek(0,0)
            f.truncate(0)
            f.write(json.dumps(_new,ensure_ascii=False,indent=4))
    except FileNotFoundError:
        # 没有找到配置文件
        with open(getPath("./config/sign.json"),mode="a+",encoding="utf-8") as f:
            # 不需要读取旧数据
            f.write(json.dumps(new_data,ensure_ascii=False,indent=4))