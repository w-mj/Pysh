# PYSH

pysh是一个基于Python语法的脚本解释程序。

## 安装

```
pip install pysh-run
```

## 使用方法

1. 基本用法 
    ```python
    from pysh.lib import Exec
    print(Exec("ls").stdout())
    ```

2. 管道
    ```python
    from pysh.lib import Exec
    print(Exec("cmd1").pipe_to(Exec("cmd2")).stdout())
    print((Exec("cmd1") | Exec("cmd2")).stdout())  # 使用管道运算符
    ```

3. 正则过滤
    ```python
    from pysh.lib import Exec, Filter
    print(Exec("cmd1").pipe_to(Filter(".*\\.ps")).stdout())
    print(Exec("cmd1").pipe_to(func).stdout())  # func的参数为cmd1的输出，输出结果为func的返回值
    ```

4. xargs
    ```python
    from pysh.lib import Exec
    Exec("lsof -i:8080").pipe_to("kill -9 $[1,1]").exec()  # 前一个命令的输出内容作为后一个命令的参数
    ```

5. &&
    ```python
    from pysh.lib import Exec
    print(Exec("cmd1").success_to(Exec("cmd2")).stdout())  # cmd1执行成功才执行cmd2
    ```

6. ||
    ```python
    from pysh.lib import Exec
    print(Exec("cmd1").fail_to(Exec("cmd2")).stdout())  # cmd1执行失败才执行cmd2
    ```

7. 流
    ```python
    from pysh.lib import Exec
    print(Exec("cmd1").stream_to(Exec("cmd2")).stdout())  # 同时启动两个进程，把cmd1的输出实时写入cmd2
    print(Exec("cmd1").stream_to(func).stdout())  # cmd1每输出一行，func被调用一次
    ```
