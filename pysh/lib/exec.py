import subprocess
import enum
import threading

from typing import List


class Exec:
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
        print("start run " + self._cmd)
        print("with input " + str(input_str))
        self._result = subprocess.run(self._cmd, input=input_str, capture_output=True)
        self._state = Exec.State.FINISHED
        print("end run " + self._cmd)

    def exec(self):
        if self._state != Exec.State.NOT_START:
            return
        threading.Thread(target=Exec.__exec_func, args=(self,)).start()
        # self.__exec_func()

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
        assert isinstance(other, Exec)
        other._input = self
        return other

    def __ror__(self, other):
        if isinstance(other, (str, Exec)):
            self._input = other
        return self
