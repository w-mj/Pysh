import subprocess
import enum
import threading
from typing import List, Callable, Union, Optional

from pysh.config import Config
import logging as log
import re

from pysh.lib.filter import Filter, RegexFilter, FuncFilter


class ResultTable:
    def __init__(self, input):
        self._input = input
        self._lines = None
        self._arr = None

    def __getitem__(self, item):
        if isinstance(item, int):
            i = item
            j = None
        else:
            i, j = item
        if j is None:
            if self._lines is None:
                self._lines = self._input.stdout().decode().split('\n')
                self._arr = [None for _ in self._lines]
            return self._lines[i]
        if self._arr is None or self._arr[i] is None:
            line = self[i].split()
            self._arr[i] = line
        return self._arr[i][j]

    def set_input(self, input):
        self._input = input


class Exec(Filter):
    class State(enum.Enum):
        NOT_START = 0
        RUNNING = 1
        FINISHED = 2
        NOT_RUN = 3

    def __init__(self, cmd: str, upstream=None, capture_output=False, pre: List['Exec'] = []):
        super().__init__(Filter.PIPE, upstream)
        self._cmd = cmd
        self._state = Exec.State.NOT_START
        self._result = None
        self._process = None
        self._upstream = upstream
        self._capture_output = capture_output
        self._pre = pre

    def __exec_func(self):
        self._state = Exec.State.RUNNING
        if self._upstream is None:
            input_str = self._upstream
        elif isinstance(self._upstream, Filter):
            if self._upstream.type in (Filter.PIPE, Filter.FUNC, Filter.FILTER):
                if self._upstream.returncode() != 0:
                    log.debug(f"pipe upstream ({self._upstream}) fail")
                    self._state = self.State.NOT_RUN
                    self._result = self._upstream.result()
                    return None
                input_str = self._upstream.stdout()
            elif self._upstream.type == Filter.IF_SUCCESS:
                if self._upstream._upstream.returncode() != 0:
                    log.debug(f"logic and upstream ({self._upstream}) fail")
                    self._state = self.State.NOT_RUN
                    # self._result = subprocess.CompletedProcess(self._cmd, self._input.upstream.returncode())
                    self._result = self._upstream.result()
                    return None
                input_str = None
            elif self._upstream.type == Filter.IF_FAIL:
                if self._upstream._upstream.returncode() == 0:
                    log.debug(f"logic or upstream ({self._upstream}) success")
                    self._state = self.State.NOT_RUN
                    # self._result = subprocess.CompletedProcess(self._cmd, self._input.upstream.returncode())
                    self._result = self._upstream.result()
                    return None
                input_str = None
            else:
                input_str = None
        elif isinstance(self._upstream, (str, bytes)):
            input_str = self._upstream
        else:
            raise Exception(f"type {type(self._upstream)} is not supported as input")
        log.debug("start run " + self._cmd)
        log.debug("with input " + str(input_str))
        self._cmd = self._parse_exec_cmd(self._cmd, self._upstream)
        self._process = subprocess.Popen(self._cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if isinstance(input_str, str):
            input_str = input_str.encode()
        if input_str:
            self._process.stdin.write(input_str)
        # self._state = Exec.State.FINISHED
        # if self._result.returncode != 0:
        #     log.info(self._result.stderr.decode())
        # log.debug("end run " + self._cmd)
        # log.debug("stdout is " + self.stdout().decode())

    def exec(self):
        if self._state != Exec.State.NOT_START:
            return

        if Config.run_in_thread:
            threading.Thread(target=Exec.__exec_func, args=(self,)).start()
        else:
            self.__exec_func()

    def join(self):
        # while self._state not in (Exec.State.FINISHED, Exec.State.NOT_RUN):
        #     pass
        if self._result:
            return
        stdout, stderr = self._process.communicate()
        self._result = subprocess.CompletedProcess(self._cmd, self._process.returncode, stdout, stderr)
        self._state = self.State.FINISHED

    def stdout(self):
        self.exec()
        self.join()
        return self._result.stdout

    def stderr(self):
        self.exec()
        self.join()
        return self._result.stderr

    def returncode(self):
        self.exec()
        self.join()
        return self._result.returncode

    def result(self):
        self.exec()
        self.join()
        return self._result

    @property
    def state(self):
        return self._state

    @property
    def input(self):
        return self._upstream

    def __or__(self, other):
        return self.set_input(other)

    def __ror__(self, other):
        if isinstance(other, (str, Exec)):
            self._upstream = other
        return self

    def run_if_fail(self, ano: 'Exec'):
        self._upstream = Filter(Filter.IF_FAIL, ano)

    def run_if_success(self, ano: 'Exec'):
        self._upstream = Filter(Filter.IF_SUCCESS, ano)

    def set_input(self, other):
        if isinstance(other, Filter):
            # 管道传递
            # other._input = self
            other._upstream = Filter(Filter.PIPE, self)
            return other
        elif isinstance(other, str):
            # 正则过滤
            def _filter(result: subprocess.CompletedProcess):
                pat = re.compile(other)
                res = pat.finditer(result.stdout)
                return '\n'.join(map(lambda x: x if isinstance(x, str) else ' '.join(x), res))

            other = FuncFilter(_filter, self)
        elif callable(other):
            other = FuncFilter(other, self)
        else:
            raise RuntimeError("Unsupported type " + other)

        return other

    def _parse_exec_cmd(self, cmd, input: Union[Filter, 'Exec']):
        arr = ResultTable(input)
        ans = ''
        state = 0
        i = None
        j = None
        for x in cmd:
            if state == 0:
                if x == '$':
                    state = 1
                else:
                    ans += x
            elif state == 1:
                if x == '$':
                    ans += '$'
                    state = 0
                elif x == '[':
                    state = 2
                    i = 0
                else:
                    ans += f'${x}'
                    state = 0
            elif state == 2:
                if str.isdigit(x):
                    i = i * 10 + int(x)
                elif x == ',':
                    j = 0
                    state = 3
                elif x == ']':
                    ans += arr[i]
                    state = 0
                elif x == ' \t':
                    pass
                else:
                    raise RuntimeError("2222")
            elif state == 3:
                if str.isdigit(x):
                    j = j * 10 + int(x)
                elif x == ']':
                    ans += arr[i, j]
                    state = 0
                elif x in ' \t':
                    pass
                else:
                    raise RuntimeError("3333")
        return ans

    def pipe_to(self, ano: Union["Filter", "Exec", str, Callable[[Optional[subprocess.CompletedProcess]], str]]):
        if isinstance(ano, str):
            ano = RegexFilter(ano)
        elif callable(ano):
            ano = FuncFilter(ano)
        ano.set_input(self)
        return ano

    def if_success(self, ano: "Exec"):
        ano.run_if_success(self)
        return ano

    def if_fail(self, ano: "Exec"):
        ano.run_if_fail(self)
        return ano
