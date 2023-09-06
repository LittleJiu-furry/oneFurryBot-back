'''
    本模块提供一个事件注册器，用来以注册器的方式通知到各个函数
'''
import msgtypes
import asyncio

class MsgBind:
    _Friend_handlers = {}
    _Group_handlers = {}
    def Friend_text(self,*bindContent:str):
        def decorator(func):
            for content in bindContent:
                bindName = "MsgBind_" + content
                if(bindName in self._Friend_handlers):
                    self._Friend_handlers[bindName].append(func)
                else:
                    self._Friend_handlers[bindName] = [func]
            return func
        return decorator

    async def friend_call(self,data:msgtypes.FriendMessage):
        _text = "MsgBind_" + (await data.msgChain.getTextMsg())
        if("MsgBind_" in self._Friend_handlers):
            for func in self._Friend_handlers["MsgBind_"]:
                next = await func(data)
                await asyncio.sleep(0)
                if(next == False):
                    return
        if(_text in self._Friend_handlers):
            for func in self._Friend_handlers[_text]:
                next = await func(data)
                await asyncio.sleep(0)
                if(next == False):
                    return
    
    def Group_text(self,*bindContent:str):
        def decorator(func):
            for content in bindContent:
                bindName = "MsgBind_" + content
                if(bindName in self._Group_handlers):
                    self._Group_handlers[bindName].append(func)
                else:
                    self._Group_handlers[bindName] = [func]
            return func
        return decorator

    async def group_call(self,data:msgtypes.GroupMessage):
        _text = "MsgBind_" + (await data.msgChain.getTextMsg())
        if("MsgBind_" in self._Group_handlers):
            for func in self._Group_handlers["MsgBind_"]:
                next = await func(data)
                await asyncio.sleep(0)
                if(next == False):
                    return
        if(_text in self._Group_handlers):
            for func in self._Group_handlers[_text]:
                next = await func(data)
                await asyncio.sleep(0)
                if(next == False):
                    return