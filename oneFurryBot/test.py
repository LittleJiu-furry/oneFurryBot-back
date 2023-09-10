import re

_fri_handler = []
def Friend_text(*pat:str):
    def deco(func):
        for p in pat:
            if('{' in p):
                # 提取其中的参数
                i = re.findall(r'\{([^\s]*)\}', p)
                print("匹配到的内容 ",i)
                # 重新构建表达式
                for rei in i:
                    p = p.replace('{'+rei+'}', '([^\s]*)')
                p = "^" + p + "$"
                _fri_handler.append((p,i,func))
            else:
                p = "^" + p + "$"
                _fri_handler.append((p,None,func))
        return func
    return deco
def friend_call(_data):
    pat = _data
    for p,i,func in _fri_handler:
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
                        if(func(_data,kwargs) == False):
                            return
                    else:
                        # 调用函数的无传参方案
                        if(func(_data) == False):
                            return
                else:
                    grep = re.findall(p,pat)
                    print(grep)
                    if(grep):
                        for prei_index in range(len(i)):
                            kwargs[i[prei_index]] = grep[0][prei_index]
                        if(func(_data,kwargs) == False):
                            return
                    else:
                        # 调用函数的无传参方案
                        if(func(_data) == False):
                            return
            else:
                if(re.match(p,pat) is not None):
                    if(func(_data) == False):
                        return
        except IndexError:
            pass


@Friend_text("#test")
def test(data,kwargs = None):
    print("test call")


friend_call("#test")