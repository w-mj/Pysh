import tokenize
from typing import List, Generator, TypeVar, NewType


class Token:
    def __init__(self, type, value, start=(0, 0), end=(0, 0), line=None):
        self.type = type
        self.value = value
        self.start = start
        self.end = end
        self.line = line

    @staticmethod
    def from_tokenize(token: tokenize.TokenInfo):
        self = Token(None, None)
        self.type = token[0]
        self.value = token[1]
        self.start = token[2]
        self.end = token[3]
        self.line = token[4]
        return self

    def to_token(self):
        return tokenize.TokenInfo(self.type, self.value, self.start, self.end, self.line)

    def __sub__(self, other):
        assert isinstance(other, Token)
        return other.end[0] - self.start[0], other.end[1] - self.start[1]

    def __str__(self):
        return str(self.to_token())

    def __repr__(self):
        return str(self)


class TokenGenerator:
    def __init__(self, tokens: Generator[tokenize.TokenInfo, None, None]):
        self._tokens = tokens
        # 已经取得但还未生成目标代码的token
        self._pre = []
        self._indent = 0

    def __getitem__(self, item: int) -> Token:
        while item >= len(self._pre):
            new = Token.from_tokenize(next(self._tokens))
            if new.type == tokenize.NEWLINE:
                self._indent = 0
            elif new.type == tokenize.INDENT:
                self._indent += 1
            self._pre.append(new)
        return self._pre[item]

    def clear(self, i=None):
        if i:
            self._pre = self._pre[i:]
        else:
            self._pre.clear()

    def keep_last_one(self):
        self.clear(len(self) - 1)

    def __len__(self):
        return len(self._pre)

    @property
    def indent(self):
        return self._indent


def _temp_generator():
    i = 0
    while True:
        i += 1
        yield f"_pysht_{i}_"


temp = _temp_generator()


class TokenList:
    def __init__(self, *data):
        self._data = list(data)
        self._var_name = None
        self._indent = 0
        self._last_var_name = None
        self._generated_name = False

    def push_front(self, data):
        assert isinstance(data, (list, TokenList))
        start = self._data[0].start
        self._data[0].start = (0, 0)
        if isinstance(data, list):
            self._data = data + self._data
        elif isinstance(data, TokenList):
            self._data = data._data + self._data
        self._data[0].start = start
        return self

    def push_back(self, data):
        assert isinstance(data, (list, TokenList))
        end = self._data[-1].end
        self._data[-1].end = (0, 0)
        if isinstance(data, list):
            self._data = self._data + data
        else:
            self._data = self._data + data._data
        self._data[-1].end = end
        return self

    def push_line(self, newline: 'TokenList'):
        self.push_back([Token(tokenize.INDENT, '\t')] * self.indent)
        self.push_back(newline)
        return self

    def eol(self):
        self._data.append(Token(tokenize.NEWLINE, '\n'))
        return self

    def newline(self):
        for x in self._data:
            x.start = (0, 0)
        return self

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item: int):
        return self._data[item]

    @property
    def var_name(self):
        if not self._var_name:
            self._var_name = next(temp)
            self._generated_name = True
        if not self._last_var_name:
            self._last_var_name = self._var_name
        return self._var_name

    @var_name.setter
    def var_name(self, value):
        self._var_name = value
        if self._last_var_name is None:
            self._last_var_name = value

    @property
    def have_name(self):
        return self._var_name is not None

    @property
    def indent(self):
        return self._indent

    @indent.setter
    def indent(self, value):
        self._indent = value

    @property
    def last_var_name(self):
        return self._last_var_name

    @last_var_name.setter
    def last_var_name(self, value):
        # print("set last var name " + value)
        self._last_var_name = value

    @property
    def generated_name(self):
        return self._generated_name

