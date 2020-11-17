import re
import subprocess
from typing import Callable, Optional, Union

import enum

from lib.FakeFile import FilterFile


class Filter:
    class State(enum.Enum):
        NOT_START = 0
        RUNNING = 1
        FINISHED = 2
        NOT_RUN = 3
    FUNC = 1
    IF_SUCCESS = 2
    IF_FAIL = 3
    PIPE = 4
    FILTER = 5
    STREAM = 6

    def __init__(self, type, upstream: Optional['Filter']):
        self._upstream = upstream
        self._type = type
        self._stdout = None
        self._stream = False

    def stdout(self):
        if self._stdout:
            return self._stdout
        self._stdout = self._upstream.stdout()
        return self._stdout

    def returncode(self):
        return self._upstream.returncode()

    def set_input(self, ano):
        self._upstream = ano

    def result(self) -> subprocess.CompletedProcess:
        return self._upstream.result()

    @property
    def state(self) -> int:
        return self._upstream.state

    @property
    def process(self) -> subprocess.Popen:
        return self._upstream.process

    @property
    def type(self):
        return self._type

    def outfile(self):
        raise RuntimeError("can not get out file")

    def set_stream(self, ano: 'Filter'):
        self._stream = True
        self.set_input(ano)

    def join(self):
        self._upstream.join()

    def __str__(self):
        return str(self.result())

    def __repr__(self):
        return str(self)


class FuncFilter(Filter):
    def __init__(self, func: Callable[[Optional[Union[subprocess.CompletedProcess, str]]], str] = None,
                 upstream: Optional['Filter'] = None):
        super().__init__(Filter.FUNC, upstream)
        self._func = func
        self._stdout = None

    def stdout(self):
        if not self._stdout:
            self._stdout = self(self._upstream.result())
        return self._stdout

    def __call__(self, arg):
        return self._func(arg)

    def outfile(self):
        return FilterFile(self._upstream.outfile(), self)


class RegexFilter(FuncFilter):
    def __init__(self, reg):
        super().__init__(None)

        def _filter(result: Optional[Union[subprocess.CompletedProcess, str]]):
            if result is None:
                return reg
            if isinstance(result, subprocess.CompletedProcess):
                result = result.stdout.decode()
            pat = re.compile(reg)
            res = pat.findall(result)
            return '\n'.join(map(lambda x: x if isinstance(x, str) else ' '.join(x), res))

        self._func = _filter
