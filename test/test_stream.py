import sys
import time

from lib.filter import Filter, RegexFilter
from pysh.lib.exec import Exec

def generate():
    for i in range(5):
        print(f"{i} {i + 1} {time.time()}")
        time.sleep(1)

def consume():
    for line in sys.stdin:
        a, b, c = line.split(' ')
        print(f"{int(a) + int(b)} {float(c)} {time.time()}")


if __name__ == '__main__':
    test_chain = ["generate", "consume"]
    test_cmd = ["python .\\test_stream.py " + x for x in test_chain]

    if len(sys.argv) == 1:
        # python .\test.py g 10 | python .\test.py c
        g = Exec(test_cmd[0])
        f = Exec(test_cmd[1])
        f.set_stream(g)
        print(g._state, f._state)
        print(f.stdout().decode())
    else:
        this_module = sys.modules[__name__]
        getattr(this_module, sys.argv[1])(*sys.argv[2:])
