import tokenize
from typing import List, Generator, TypeVar, NewType
import logging as log


out = open('out.txt', 'w')

def _search_indents(line):
    indents = 0
    spaces = 0
    for c in line:
        if c == '\t':
            indents += 1
        elif c == ' ':
            if spaces == 3:
                indents += 1
                spaces = 0
            else:
                spaces += 1
        else:
            assert False
    return indents


class Token:

    def __init__(self, type, value:str, start=(0, 0), end=(0, 0), line=None):
        assert not isinstance(value, Token)
        assert value is not None
        self.type = type
        self.value = value
        self.start = start
        self.end = end
        self.line = line

    @staticmethod
    def from_tokenize(token: tokenize.TokenInfo):
        self = Token(None, '')
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


class Line:
    def __init__(self):
        self._data: List[Token] = []
        self._indent = 0

    def add_token(self, token: Token):
        if token.type not in (tokenize.INDENT, tokenize.DEDENT):
            self._data.append(token)

    @property
    def indent(self):
        return self._indent

    # @indent.setter
    # def indent(self, val):
    #     self._indent = val

    @property
    def data(self):
        return self._data

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item):
        return self._data[item]


class TokenGenerator:
    def __init__(self, tokens: Generator[tokenize.TokenInfo, None, None]):
        self._tokens = tokens
        # 已经取得但还未生成目标代码的token
        self._pre = []
        self._indent = 0

    def __getitem__(self, item: int) -> Token:
        while item >= len(self._pre):
            new = Token.from_tokenize(next(self._tokens))
            print(new, file=out)
            # if new.type == tokenize.NEWLINE:
            #     self._indent = 0
            # elif new.type == tokenize.INDENT:
            #     self._indent += _search_indents(new.value)
            if new.type == tokenize.INDENT:
                self._indent += 1
            elif new.type == tokenize.DEDENT:
                self._indent -= 1
            self._pre.append(new)
        return self._pre[item]

    def clear(self, i=None):
        if i:
            self._pre = self._pre[i:]
        else:
            self._pre.clear()

    def push_front(self, item):
        if isinstance(item, TokenList):
            self._pre = item._data + self._pre
        else:
            self._pre.insert(0, item)

    def keep_last_one(self):
        self.clear(len(self) - 1)

    def __len__(self):
        return len(self._pre)

    @property
    def indent(self):
        return self._indent

    def get_next_line(self):
        i = 0
        line = Line()
        while True:
            line.add_token(self[i])
            if self[i].type in (tokenize.NEWLINE, tokenize.ENDMARKER, tokenize.NL):
                break
            i += 1
        line._indent = self.indent
        return line


def _temp_generator():
    i = 0
    while True:
        i += 1
        yield f"_pysht_{i}_"


temp_name = _temp_generator()


class TokenList:
    Exec = 1
    Filter = 2
    Normal = 3
    FULL = 4
    SWITCH = 5

    def __init__(self, data, indent, type=3):
        self._data = list(data)
        self._var_name = None
        self._indent = indent
        self._last_var_name = None
        self._generated_name = False
        self.type = type

        last = None
        for x in self._data:
            if not last or last.type in (tokenize.NL, tokenize.NEWLINE):
                if x.start[1] != indent * 4:
                    x.start = (x.start[1], indent * 4)
            last = x
        # if self._data:
        #     self._data = [Token(tokenize.INDENT, '    ' * indent, start=(data[0].start[0], 0), end=(data[0].end[0], 4 * indent))] + self._data

    def push_front(self, data):
        assert isinstance(data, (list, TokenList))
        start = self._data[0].start
        self._data[0].start = (0, 0)
        if isinstance(data, list):
            self._data = data + self._data
        elif isinstance(data, TokenList):
            # self._data = data._data + self._data
            data.push_back(self)
            # self = data  # 魔鬼操作
            return data
        self._data[0].start = start
        return self

    def push_back(self, data):
        assert isinstance(data, (list, TokenList))
        if self._data:
            end = self._data[-1].end
            self._data[-1].end = (0, 0)
        else:
            end = (0, 0)
        if isinstance(data, list):
            self._data = self._data + data
        else:
            self._data = self._data + data._data
            # first = True
            # for i in range(len(data._data)):
            #     x = data._data[i]
            #     if first and data.indent > self._indent:
            #         self._data += [Token(tokenize.INDENT, '\t')] * (data.indent - self._indent)
            #         first = False
            #     if x.type == tokenize.NEWLINE:
            #         self._data.append(x)
            #         if i != len(data._data) - 1:
            #             self._data += [Token(tokenize.INDENT, '\t')] * max(data.indent - self._indent, 0)
            #     else:
            #         self._data.append(x)
        if self._data:
            self._data[-1].end = end
        return self

    def push_line(self, newline: 'TokenList'):
        # self.push_back([Token(tokenize.INDENT, '\t')] * self.indent)
        self.push_back(newline)
        return self

    def eol(self):
        self._data.append(Token(tokenize.NEWLINE, '\n'))
        return self

    def newline(self):
        if not self._data:
            return
        x_offset = self._data[0].start[1]
        for x in self._data:
            x.start = (x.start[0], x.start[1] - x_offset)
            x.end = (x.end[0], x.end[1] - x_offset)
        return self

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, item: int):
        return self._data[item]

    @property
    def var_name(self):
        if not self._var_name:
            self.generate_name()
        if not self._last_var_name:
            self._last_var_name = self._var_name
        return self._var_name

    def generate_name(self):
        self._var_name = next(temp_name)
        self._generated_name = True

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

