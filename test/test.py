from sys import stdin
import sys
from pysh.lib.exec import Exec


def generate(n):
    for i in range(int(n)):
        print(f"{i} {i+1}")

def consume():
    for line in stdin:
        a, b = line.split(' ')
        print(int(a) + int(b))

def add(a, b):
    print(int(a) + int(b))

def hello():
    print("hello world")

def fail():
    print("fail")
    exit(-1)


if __name__ == '__main__':
    test_chain = ["generate 10", "consume", "fail", "hello", "add $[2,0] $[2,1]"]

    test_cmd = ["python test.py " + x for x in test_chain]
    if len(sys.argv) == 1:
        t = Exec("python test.py generate 10")
        print(t.stdout())
        print("abcdef")
        # python .\test.py g 10 | python .\test.py c
        t = Exec(test_cmd[0]) | Exec(test_cmd[1])
        print(t._cmd)
        print(t.stdout())

        t = Exec(test_cmd[0]) | Exec(test_cmd[4])
        # print(t._cmd)
        print(t.stdout())

        t1 = Exec(test_cmd[2])
        t2 = Exec(test_cmd[3])
        t2.run_if_fail(t1)
        print(t2.stdout())
    else:
        this_module = sys.modules[__name__]
        getattr(this_module, sys.argv[1])(*sys.argv[2:])

