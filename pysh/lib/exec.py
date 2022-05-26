import subprocess
import enum
import threading
from typing import List, Callable, Union, Optional

from pysh.lib.FakeFile import RealFile, FakeFile
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

    def __init__(self, cmd: str, upstream=None, capture_output=False, pre=None):
        super().__init__(Filter.PIPE, upstream)
        if pre is None:
            pre = []
        self._cmd = cmd
        self._state = Exec.State.NOT_START
        self._result = None
        self._process = None
        self._upstream = upstream
        self._capture_output = capture_output
        self._pre = pre

    def __exec_func(self):
        self._state = Exec.State.RUNNING
        input_file: FakeFile = self._upstream.outfile() if self._stream else None
        if not input_file:
            if self._upstream is None:
                input_str = None
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
            self._process = subprocess.Popen(self._cmd, shell=True,
                                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if isinstance(input_str, str):
                input_str = input_str.encode()
            if input_str:
                self._process.stdin.write(input_str)
        else:
            # 流
            log.debug("start run stream " + self._cmd)
            self._process = subprocess.Popen(self._cmd, shell=True,
                                             stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            def _pass():
                while True:
                    line = input_file.readline()
                    if line in ('', b''):
                        self._state = Exec.State.FINISHED
                        break
                    if isinstance(line, str):
                        line = line.encode()
                    self._process.stdin.write(line)
                    self._process.stdin.flush()
                    log.debug(f"write {line} to process")
                log.debug("quit thread")
            threading.Thread(target=_pass).start()

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
        if self._upstream:
            self._upstream.join()
        # stdout, stderr = self._process.communicate()
        self._process.stdin.close()
        retc = None
        while retc is None:
            retc = self._process.poll()
        log.debug(f"process {self._process.pid} finish with " + str(retc))
        stdout = self._process.stdout.read()
        stderr = self._process.stderr.read()
        # log.debug("process finish with " + str(retc))
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
    def process(self):
        return self._process

    @property
    def input(self):
        return self._upstream

    def outfile(self):
        if self._state == Exec.State.NOT_START:
            self.exec()
        return RealFile(self._process.stdout)

    def errfile(self):
        if self._state == Exec.State.NOT_START:
            self.exec()
        return RealFile(self._process.stderr)

    def __or__(self, other):
        other.set_input(self)
        return other

    def __ror__(self, other):
        if isinstance(other, (str, Exec)):
            self._upstream = other
        return self

    def run_if_fail(self, ano: 'Exec'):
        self._upstream = Filter(Filter.IF_FAIL, ano)

    def run_if_success(self, ano: 'Exec'):
        self._upstream = Filter(Filter.IF_SUCCESS, ano)

    def set_input(self, other):
        self._upstream = other
        return other

    def set_stream_input(self, other):
        self.set_stream(other)

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

    def stream_to(self, ano):
        ano.set_stream(self)
        return ano

    def success_to(self, ano: "Exec"):
        ano.run_if_success(self)
        return ano

    def fail_to(self, ano: "Exec"):
        ano.run_if_fail(self)
        return ano
