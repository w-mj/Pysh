import subprocess
import enum
import threading
from typing import List, Callable

from pysh.config import Config
import logging as log
import re


class Exec:
    class OutputFilter:
        def __init__(self, upstream: 'Exec', func: Callable[[subprocess.CompletedProcess], str]):
            self.upstream = upstream
            self.func = func

        def __call__(self):
            return self.func(self.upstream.result())

    class State(enum.Enum):
        NOT_START = 0
        RUNNING = 1
        FINISHED = 2

    def __init__(self, cmd: str, input=None, capture_output=False, pre: List['Exec']=[]):
        self._cmd = cmd
        self._state = Exec.State.NOT_START
        self._result = None
        self._input = input
        self._capture_output = capture_output
        self._pre = pre

    def __exec_func(self):
        self._state = Exec.State.RUNNING
        if self._input is None:
            input_str = self._input
        elif isinstance(self._input, Exec):
            input_str = self._input.stdout()
        elif isinstance(self._input, str):
            input_str = self._input
        else:
            raise Exception(f"type {type(self._input)} is not supported as input")
        log.debug("start run " + self._cmd)
        log.debug("with input " + str(input_str))
        self._result = subprocess.run(self._cmd, input=input_str, capture_output=True)
        self._state = Exec.State.FINISHED
        log.debug("end run " + self._cmd)

    def exec(self):
        if self._state != Exec.State.NOT_START:
            return

        if Config.run_in_thread:
            threading.Thread(target=Exec.__exec_func, args=(self,)).start()
        else:
            self.__exec_func()

    def join(self):
        while self._state != Exec.State.FINISHED:
            pass

    def stdout(self):
        self.exec()
        self.join()
        return self._result.stdout

    def stderr(self):
        self.exec()
        self.join()
        return self._result.stderr

    def result(self):
        self.exec()
        self.join()
        return self._result

    @property
    def state(self):
        return self._state

    @property
    def input(self):
        return self._input

    @input.setter
    def input(self, value):
        self._input = value

    def __or__(self, other):
        if isinstance(other, Exec):
            # 管道传递
            other._input = self
            return other
        elif isinstance(other, str):
            # 正则过滤
            def _filter(result: subprocess.CompletedProcess):
                pat = re.compile(other)
                res = pat.finditer(result.stdout)
                return '\n'.join(map(lambda x: x if isinstance(x, str) else ' '.join(x), res))
            other._input = Exec.OutputFilter(self, _filter)
        elif callable(other):
            other._input = Exec.OutputFilter(self, other)

    def __ror__(self, other):
        if isinstance(other, (str, Exec)):
            self._input = other
        return self
