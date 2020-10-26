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


class TokenList:
    def __init__(self, *data):
        self.data = list(data)

    def push_front(self, data):
        assert isinstance(data, (list, TokenList))
        start = self.data[0].start
        if isinstance(data, list):
            self.data = data + self.data
        elif isinstance(data, TokenList):
            self.data = data.data + self.data
        self.data[0].start = start
        return self

    def push_back(self, data):
        assert isinstance(data, (list, TokenList))
        end = self.data[-1].end
        if isinstance(data, list):
            self.data = self.data + data
        else:
            self.data = self.data + data.data
        self.data[-1].end = end
        return self

    def push_line(self, newline: 'TokenList', indent):
        self.push_back([Token(tokenize.INDENT, '\t')] * indent * 4)
        self.push_back(newline)
        return self

    def eol(self):
        self.data.append(Token(tokenize.NEWLINE, '\n'))
        return self

    def newline(self):
        for x in self.data:
            x.start = (0, 0)
        return self

    def __iter__(self):
        return iter(self.data)

    def __getitem__(self, item: int):
        return self.data[item]


