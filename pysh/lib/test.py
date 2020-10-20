from sys import stdin
import sys
from pysh.lib.exec import Exec
import subprocess


def generate(n):
    for i in range(n):
        print(f"{i} {i+1}")


def consume():
    for line in stdin:
        a, b = line.split(' ')
        print(int(a) + int(b))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # python .\test.py g 10 | python .\test.py c
        t = Exec("python .\\test.py g 10") | Exec("python .\\test.py c")
        print(t._cmd)
        print(t.stdout())
    elif sys.argv[1] == 'g':
        generate(int(sys.argv[2]))
    elif sys.argv[1] == 'c':
        consume()
