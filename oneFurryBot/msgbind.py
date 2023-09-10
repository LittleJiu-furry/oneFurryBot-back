'''
    本模块提供一个事件注册器，用来以注册器的方式通知到各个函数
'''
import msgtypes
import asyncio
import re

# class MsgBind:
#     _Friend_handlers = {}
#     _Group_handlers = {}
#     def Friend_text(self,*bindContent:str):
#         def decorator(func):
#             for content in bindContent:
#                 bindName = "MsgBind_" + content
#                 if(bindName in self._Friend_handlers):
#                     self._Friend_handlers[bindName].append(func)
#                 else:
#                     self._Friend_handlers[bindName] = [func]
#             return func
#         return decorator

#     async def friend_call(self,data:msgtypes.FriendMessage):
#         _text = "MsgBind_" + (await data.msgChain.getTextMsg())
#         if("MsgBind_" in self._Friend_handlers):
#             for func in self._Friend_handlers["MsgBind_"]:
#                 next = await func(data)
#                 await asyncio.sleep(0)
#                 if(next == False):
#                     return
#         if(_text in self._Friend_handlers):
#             for func in self._Friend_handlers[_text]:
#                 next = await func(data)
#                 await asyncio.sleep(0)
#                 if(next == False):
#                     return
    
#     def Group_text(self,*bindContent:str):
#         def decorator(func):
#             for content in bindContent:
#                 bindName = "MsgBind_" + content
#                 if(bindName in self._Group_handlers):
#                     self._Group_handlers[bindName].append(func)
#                 else:
#                     self._Group_handlers[bindName] = [func]
#             return func
#         return decorator

#     async def group_call(self,data:msgtypes.GroupMessage):
#         _text = "MsgBind_" + (await data.msgChain.getTextMsg())
#         if("MsgBind_" in self._Group_handlers):
#             for func in self._Group_handlers["MsgBind_"]:
#                 next = await func(data)
#                 await asyncio.sleep(0)
#                 if(next == False):
#                     return
#         if(_text in self._Group_handlers):
#             for func in self._Group_handlers[_text]:
#                 next = await func(data)
#                 await asyncio.sleep(0)
#                 if(next == False):
#                     return
                
class MsgBind:
    _fri_handler = []
    _gro_handler = []
    def Friend_text(self,*pat:str):
        def deco(func):
            for p in pat:
                if('{' in p):
                    # 提取其中的参数
                    i = re.findall(r'\{([^\s]*)\}', p)
                    print("匹配到的内容 ",i)
                    # 重新构建表达式
                    for rei in i:
                        p = p.replace('{'+rei+'}', '([^\s]*)')
                    self._fri_handler.append((p,i,func))
                else:
                    self._fri_handler.append((p,None,func))
            return func
        return deco

    async def friend_call(self,_data:msgtypes.FriendMessage):
        pat = await _data.msgChain.getTextMsg()
        for p,i,func in self._fri_handler:
            try:
                # 对参数进行替换
                # 构建参数传递字典
                kwargs = {}
                if(i is not None):
                    if(len(i) == 1):
                        grep = re.findall(p,pat)
                        print(grep)
                        if(grep):
                            for prei_index in range(len(i)):
                                kwargs[i[prei_index]] = grep[prei_index]
                            if(await func(_data,kwargs) == False):
                                return
                        else:
                            # 调用函数的无传参方案
                            if(await func(_data) == False):
                                return
                    else:
                        grep = re.findall(p,pat)
                        print(grep)
                        if(grep):
                            for prei_index in range(len(i)):
                                kwargs[i[prei_index]] = grep[0][prei_index]
                            if(await func(_data,kwargs) == False):
                                return
                        else:
                            # 调用函数的无传参方案
                            if(await func(_data) == False):
                                return
                else:
                    if(re.findall(p,pat)[0] == p):
                        if(await func(_data) == False):
                            return
            except IndexError:
                pass
            await asyncio.sleep(0)

    def Group_text(self,*pat:str):
        def deco(func):
            for p in pat:
                if('{' in p):
                    # 提取其中的参数
                    i = re.findall(r'\{([^\s]*)\}', p)
                    print("匹配到的内容 ",i)
                    # 重新构建表达式
                    for rei in i:
                        p = p.replace('{'+rei+'}', '([^\s]*)')
                    self._gro_handler.append((p,i,func))
                else:
                    self._gro_handler.append((p,None,func))
            return func
        return deco

    async def group_call(self,_data:msgtypes.GroupMessage):
        pat = await _data.msgChain.getTextMsg()
        for p,i,func in self._gro_handler:
            # 对参数进行替换
            # 构建参数传递字典
            try:
                kwargs = {}
                if(i is not None):
                    if(len(i) == 1):
                        grep = re.findall(p,pat)
                        print(grep)
                        if(grep):
                            for prei_index in range(len(i)):
                                kwargs[i[prei_index]] = grep[prei_index]
                            if(await func(_data,kwargs) == False):
                                return
                        else:
                            # 调用函数的无传参方案
                            if(await func(_data) == False):
                                return
                    else:
                        grep = re.findall(p,pat)
                        print(grep)
                        if(grep):
                            for prei_index in range(len(i)):
                                kwargs[i[prei_index]] = grep[0][prei_index]
                            if(await func(_data,kwargs) == False):
                                return
                        else:
                            # 调用函数的无传参方案
                            if(await func(_data) == False):
                                return
                else:
                    if(re.findall(p,pat)[0] == p):
                        if(await func(_data) == False):
                            return
            except IndexError:
                pass
            await asyncio.sleep(0)


