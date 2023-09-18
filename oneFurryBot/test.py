async def abc(test):
    # print(test2)
    a = 0
    pass


# abc(**{"test":123,"a":None,"b":None})
print(abc.__code__.co_varnames[:abc.__code__.co_argcount])