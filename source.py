# coding:pysh
import pysh.lib

if 1:
    print(1)
    if 2:
        print(2)
        if 3:
            print(3)
        print(2)
    print(1)

def f1():
    t =  e"ps '-ef '" | g'grep "nginx"' | balabala && e"a" || e"b" | Class
    return t


a = f"123{abc}"
e "ls -l"
asd = e"hahahaha ${a} $1[1][2]"
e = abc | "asdasd" | e"bbaa"
Exec("ls -l")

"input"| e"ps"

for i in range(10):
    print(i)
# for j in e'ls':
#     print(j)
abc | 1
e"only one"

if callable(lambda x: x + 1):
    (lambda x: x + 1)(1)

a = 1.5

switch a:
    1 -> print('=1')
        print('=1 2')
    [1, 2] -> print('[1,2]')
    [1,] -> print('[1,]')
        print('[1,] 2')
    [,2] ->
        print('[,2]')
        print('[,2]2')
    (1, 3) -> print('(1,3)')
    (1,) -> print('(1,)')
    (, 3) -> print('(,3)')
print(000)

a = e"python .\test_filter.py generate" | g"+\.ps"
print(a.stdout())

a = e"python ./test.py generate 10" | e"python ./test.py consume"
print(a.stdout())

a = e"python ./test.py generate 10"
print("run a")
b = a | e"python ./test.py consume"
c = a | e"python ./test.py consume"
print(b.stdout())
print(c.stdout())

a = e"python ./test.py generate 10" | "python ./test.py add $[2,0] $[2,1]"
print(a.stdout())

a = e"python ./test.py fail" && e"python ./test.py hello"
print(a.stdout())

a = e"python ./test.py fail" || e"python ./test.py hello"
print(a.stdout())

a = e"python ./test_stream.py generate" ~ e"python ./test_stream.py consume"
print(a.stdout())

def _f(x: str):
    print("FFF", x, time.time())
    return x
a = e"python ./test_stream.py generate" ~ _f
print(a.stdout())
