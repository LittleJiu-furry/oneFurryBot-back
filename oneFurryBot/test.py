import re

a = "MSGBIND_123456"
print(a[8:])
exit()

_handler = []
def Friend_text(*pat:str):
    def deco(func):
        for p in pat:
            if('{' in p):
                # 提取其中的参数
                i = re.findall(r'\{([^\s]*)\}', p)
                # 重新构建表达式
                for rei in i:
                    p = p.replace(' {'+rei+'}', '( (?=[^\s])[^\s]*){1}')
                p = "^" + p + "$"
                _handler.append((p,i,func))
            else:
                p = "^" + p + "$"
                _handler.append((p,None,func))
        return func
    return deco
def friend_call(_data):
    pat = _data
    for p,i,func in _handler:
        if(i is not None):
            # 有参数列表
            grep = re.match(p,pat)
            if(grep is not None):
                grepList = grep.groups()
                kwargs = {}
                for args in grepList:
                    kwargs[i[grepList.index(args)]] = args
                func(_data,kwargs)
            else:
                continue
        else:
            if(re.match(p,pat) != None):
                func(_data)
            
            


@Friend_text("test")
def test(data,a:dict = None):
    print(f"data: {data}\na: {a}")


friend_call("")