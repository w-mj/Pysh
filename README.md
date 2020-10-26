# PYSH

pysh是一个基于Python语法的脚本解释程序。

## 计划语法

### 0.通过e字符串执行外部命令（语法）

```
e"ls"
```

e字符串会被解析成可执行外部命令的对象(Exec)。以上语句应执行外部命令ls。返回执行的结果（stdout、stderr、return code等）

可执行对象最好能做成延迟计算（待定）。

e字符串默认包含f字符串语义。

### 1. 管道运算符

```
e"ps -ef" | e'grep "nginx"'
```

管道运算符可以将程序的输出传递给字符串，此时第一个执行的stdout作为第二个执行的stdin。

当|运算符两侧类型为整数时，依然作为按位或。

```
def operator|(Exec e1, Exec e2):
	# 执行e1，将stdout作为e2的stdin
	return e2
def opeartor|(str s1, Exec e2):
	# 将s1作为e2的stdin
	return e2
def operator|(Exec e1, str s2):
	# 使用s2描述的正则表达式过滤e1的输出
```

### 2. 获得外部命令结果

```
result = e"ps -ef".stdout
```

### 3. 参数结构体（语法）

```
Args arg1(prefix=--, abbr=true, deli=' '):
	f = filter
	D = INPUT
	p = tcp
	m = state
	state = NEW
	m = tcp
	dport = 22
	j = ACCEPT
e"iptables ${arg1}"
```

以上代码会被编译成"iptables -f filter -D INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT"

Args类型应被看作是字符串的另一种描述方式，应在编译期将其转换为字符串。

### 4. 正则表达式字面量（语法）

```
e"ps -ef" | g"^user.+" | e"some command else"
```

作为管道参数的字符串会被解析成正则表达式，将第一个命令的stdout经过正则过滤后传递给下一个命令。

暂时不支持匹配组，若匹配到多个，将多个结果强行拼接到一起。

经正则表达式过滤后得到的结果为字符串。

### 5. 对象模板（语法）

```
template PsResult: "${PID}\s+${TTY}\s+${TIME}\s+${CMD}"
res = e"ps" | PsResult
```

以上代码将ps命令的输出按PsResult的匹配，返回PsResult的对象或数组。以上代码应该被编译成下面的样子（大概）

```python
class PsResult:
	def __init__(self, PID, TTY, TIME, CMD):
        self.PID = PID
        self.TTY = TTY
        self.TIME = TIME
        self.CMD = CMD
    @classmethod
    def generate(s):
        pattern = re.compile(r"(.+?)\s+(.+?)\s+(.+?)\s+(.+?)")
        res = re.findall(pattern, s)
        return [PsResult(**x[1:]) for x in res]  # 这瞎写的
```

### 6.Makefile功能(待议)

```
lib.a -> func.o main.o
(.+)\.o -> $1.c
(.+)\.c -> 
```

### 7. xargs功能（语法）

```
lsof -i:8080 | sed '2p' | awk '{print $1}' | xargs -x kill -9
e"lsof -i:8080" | e"kill -9 $1[1,1]"
```

在e字符串中，使用\$1表示前一个命令的stdout，使用\$1[0]表示输出的第1行，使用\$1[0, 0]表示输出的第一行第一列。以空白符（空格和制表符）作为分割列的标志。

应进行语义分析，若后续程序中未使用\$1变量，则不对前一个程序的输出进行分割处理，以节省资源。

同样，使用$2表示前一个命令的stderr，使用$?表示前一个命令的返回值。

### 8. 参数中的列表和字典（语法）

```
lst = [1, 2, 3]
e"prog ${lst}" 应执行 prog 1 2 3
dic = {'a': 1, 'arg': 'balabala', 'lst': [1, 3]}
e"prog ${dic}" 应执行 prog -a 1 --arg balabala --lst 1 3
```

也应该可以指定在字典情形时的参数前缀和分隔符。

生成参数在Exec对象构造时进行，即之后再修改lst中的内容不应再影响程序的参数。

### 9. 给Python加个Switch（语法）

```
s = "123"
switch(s):
	123 : func1()
	"456" :
		func1()
		func2()
	default : s + 1
```

```python
s = "123"
if s == 123:
    func1()
elif s == "456":
    func1()
    func2()
else:
    s + 1
```

### 10. 添加python静态变量（语法）
```
def func1(a, b)
	static c = 1
	c += 1
	balabala
```

```python
class static_class_func1:
    def __init__(self):
        self.c = 1
    def __call__(self, a, b):
        self.c += 1
        balabala
func1 = static_class_func1()
```

## 文法
```
`statement -> <e-statement>
e-statement -> <e-obj>| <e-obj><oper><e-obj>
e-obj -> [e|g]<str> | <e-tuple>
oper -> | && || ~
e->tuple -> e<str>{,e<str>}
```