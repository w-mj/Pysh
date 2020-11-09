import subprocess
import enum
import threading
from typing import List, Callable

from pysh.config import Config
import logging as log
import re

from pysh.lib.filter import Filter


class Exec:
    class State(enum.Enum):
        NOT_START = 0
        RUNNING = 1
        FINISHED = 2

    def __init__(self, cmd: str, input=None, capture_output=False, pre: List['Exec'] = []):
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
        elif isinstance(self._input, Filter):
            if self._input.type == Filter.PIPE:
                input_str = self._input.upstream.stdout()
            elif self._input.type == Filter.FUNC:
                input_str = self._input()
            elif self._input.type == Filter.IF_SUCCESS:
                if self._input.upstream.returncode() != 0:
                    return None
                input_str = None
            elif self._input.type == Filter.IF_NOT_SUCCESS:
                if self._input.upstream.returncode() == 0:
                    return None
                input_str = None
            else:
                input_str = None
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
        return self._input

    @input.setter
    def input(self, value):
        self._input = value

    def __or__(self, other):
        if isinstance(other, Exec):
            # 管道传递
            # other._input = self
            other._input = Filter(Filter.PIPE, self)
            return other
        elif isinstance(other, str):
            # 正则过滤
            def _filter(result: subprocess.CompletedProcess):
                pat = re.compile(other)
                res = pat.finditer(result.stdout)
                return '\n'.join(map(lambda x: x if isinstance(x, str) else ' '.join(x), res))

            other._input = Filter(Filter.FUNC, self, _filter)
        elif callable(other):
            other._input = Filter(Filter.FUNC, self, other)

    def __ror__(self, other):
        if isinstance(other, (str, Exec)):
            self._input = other
        return self

    def run_if_not_success(self, ano: 'Exec'):
        self._input = Filter(Filter.IF_NOT_SUCCESS, ano)

    def run_if_success(self, ano: 'Exec'):
        self._input = Filter(Filter.IF_SUCCESS, ano)

    def set_input(self, ano):
        self._input = ano
