#
# class Template:
#     def __init__(self, reg):
#         self._reg = reg
#         self.var_t = 2
#
#     def add(self):
#         setattr(self, 'ttt', '123')
#
#
# class Clz(Template):
#     def __init__(self):
#         super().__init__("1")
#         self.var_c = 1
#
#
# c = Clz()
# print(c.__dict__)
# c.add()
# print(c.__dict__)
# import re
# a = """
# total 17
# -rw-r--r-- 1 wsl wsl 1093 Aug 31 11:17 1.ps
# -rw-r--r-- 1 wsl wsl  552 Aug 31 11:17 2.ps
# -rw-r--r-- 1 wsl wsl  437 Aug 31 11:17 3.ps
# -rw-r--r-- 1 wsl wsl  199 Aug 27 11:58 a.c
# -rw-r--r-- 1 wsl wsl 1880 Aug 27 11:58 a.o
# -rw-r--r-- 1 wsl wsl 5360 Aug 31 11:39 temp.ps
# """
# p = re.compile(r"([a-z\-]+)\s+(\d+)\s+(.+)\s+(.+)\s+(.+)\s+(.+)\s+(.+)\s+(.+)\s+(.+)\s+", re.MULTILINE)
# r = p.findall(a)
# print(r)

def check_switch_case_condition(a, b):
    if callable(b):
        return b(a)
    return a == b