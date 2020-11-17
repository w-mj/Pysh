import re
import subprocess
from typing import Callable, Optional


class Filter:
    FUNC = 1
    IF_SUCCESS = 2
    IF_FAIL = 3
    PIPE = 4
    FILTER = 5

    def __init__(self, type, upstream: Optional['Filter']):
        self._upstream = upstream
        self.type = type
        self._stdout = None

    def stdout(self):
        if self._stdout:
            return self._stdout
        self._stdout = self._upstream.stdout()
        return self._stdout

    def returncode(self):
        return self._upstream.returncode()

    def set_input(self, ano):
        self._upstream = ano

    def result(self):
        return self._upstream.result()

    def __str__(self):
        return str(self.result())

    def __repr__(self):
        return str(self)


class FuncFilter(Filter):
    def __init__(self, func: Callable[[Optional[subprocess.CompletedProcess]], str] = None, upstream: Optional['Filter']=None):
        super().__init__(Filter.FUNC, upstream)
        self._func = func
        self._stdout = None

    def stdout(self):
        if not self._stdout:
            self._stdout = self._func(self._upstream)
        return self._stdout


class RegexFilter(FuncFilter):
    def __init__(self, reg):
        super().__init__(None)

        def _filter(result: Optional[subprocess.CompletedProcess]):
            if result is None:
                return reg
            pat = re.compile(reg)
            res = pat.findall(result.stdout().decode())
            return '\n'.join(map(lambda x: x if isinstance(x, str) else ' '.join(x), res))
        self._func = _filter
