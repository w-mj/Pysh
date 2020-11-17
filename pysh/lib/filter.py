import re
import subprocess
from typing import Callable, Optional


class Filter:
    FUNC = 1
    IF_SUCCESS = 2
    IF_FAIL = 3
    PIPE = 4
    FILTER = 5

    def __init__(self, type, upstream, func: Callable[[Optional[subprocess.CompletedProcess]], str] = None):
        self.upstream = upstream
        self.func = func
        self.type = type
        self._stdout = None

    def __call__(self):
        if self.upstream:
            return self.func(self.upstream)
        return self.func(None)

    def stdout(self):
        if self._stdout:
            return self._stdout
        if self.type in (self.FUNC, self.FILTER):
            self._stdout = self()
        else:
            self._stdout = self.upstream.stdout()
        return self._stdout

    def returncode(self):
        return self.upstream.returncode()

    def set_input(self, ano):
        self.upstream = ano

    def result(self):
        return self.upstream.result()

    def __str__(self):
        return str(self.result())

    def __repr__(self):
        return str(self)


class RegexFilter(Filter):
    def __init__(self, reg):
        super().__init__(Filter.FUNC, None)

        def _filter(result: subprocess.CompletedProcess):
            if result is None:
                return reg
            pat = re.compile(reg)
            res = pat.findall(result.stdout().decode())
            return '\n'.join(map(lambda x: x if isinstance(x, str) else ' '.join(x), res))

        self.func = _filter


class FuncFilter(Filter):
    def __init__(self, func):
        super().__init__(Filter.FUNC, None, func)

