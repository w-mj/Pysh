import io


class FakeFile:
    def __init__(self):
        pass

    def readline(self):
        pass


class RealFile(FakeFile):
    def __init__(self, fd: io.TextIOWrapper):
        super().__init__()
        self._fd = fd

    def readline(self):
        return self._fd.readline()


class FilterFile(FakeFile):
    def __init__(self, upstream: FakeFile, node):
        super(FilterFile, self).__init__()
        self._fd = upstream
        self._node = node

    def readline(self):
        return self._node(self._fd.readline())
