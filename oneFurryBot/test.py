import re

_handler = []
def reg(*pat:str):
    def deco(func):
        for p in pat:
            if('{' in p):
                # 提取其中的参数
                i = re.findall(r'\{([^\s]*)\}', p)
                print("匹配到的内容 ",i)
                # 重新构建表达式
                for rei in i:
                    p = p.replace('{'+rei+'}', '([^\s]*)')
                _handler.append((p,i,func))
            else:
                _handler.append((p,None,func))
        return func
    return deco

def reg_deal(pat:str):
    for p,i,func in _handler:
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
                    func(kwargs)
                else:
                    # 调用函数的无传参方案
                    func(None)
            else:
                grep = re.findall(p,pat)
                print(grep)
                if(grep):
                    for prei_index in range(len(i)):
                        kwargs[i[prei_index]] = grep[0][prei_index]
                    func(kwargs)
                else:
                    # 调用函数的无传参方案
                    func(None)
        else:
            if(re.findall(p,pat)[0] == p):
                func(None)
            
                
                
@reg("")
def test(args):
    if(args is not None):
        print("接收到a ",args)
    else:
        print("没有a的值")


reg_deal("test")