from sys import stdin
import sys

from pysh.lib.filter import Filter, RegexFilter
from pysh.lib.exec import Exec

a = """
total 17
-rw-r--r-- 1 wsl wsl 1093 Aug 31 11:17 1.ps
-rw-r--r-- 1 wsl wsl  552 Aug 31 11:17 2.ps
-rw-r--r-- 1 wsl wsl  437 Aug 31 11:17 3.ps
-rw-r--r-- 1 wsl wsl  199 Aug 27 11:58 a.c
-rw-r--r-- 1 wsl wsl 1880 Aug 27 11:58 a.o
-rw-r--r-- 1 wsl wsl 5360 Aug 31 11:39 temp.ps
"""

def generate():
    print(a)


if __name__ == '__main__':
    test_chain = ["generate"]
    test_cmd = ["python .\\test_filter.py " + x for x in test_chain]

    if len(sys.argv) == 1:
        # python .\test.py g 10 | python .\test.py c
        g = Exec(test_cmd[0])
        f = RegexFilter(r".+\.ps")
        f.set_input(g)
        print(f.stdout())
    else:
        this_module = sys.modules[__name__]
        getattr(this_module, sys.argv[1])(*sys.argv[2:])
