import time

t = time.localtime(time.time())
print(t)
print(t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, t.tm_sec)