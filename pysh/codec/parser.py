# token: type, value, (start), (end), line
import tokenize
from .excepts import NoneOfMyBusiness


class Token:
    def __init__(self, type, value, start=(0, 0), end=(0, 0), line=None):
        self.type = type
        self.value = value
        self.start = start
        self.end = end
        self.line = line

    @staticmethod
    def from_tokenize(token):
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
    def __init__(self, tokens):
        self.tokens = tokens
        # 已经取得但还未生成目标代码的token
        self.pre = []
        self.cursor = -1

    def __getitem__(self, item) -> Token:
        while item >= len(self.pre):
            self.pre.append(Token.from_tokenize(next(self.tokens)))
        return self.pre[item]

    def clear(self, i=None):
        if i:
            self.pre = self.pre[i:]
        else:
            self.pre.clear()

    def keep_last_one(self):
        self.clear(len(self) - 1)

    def __len__(self):
        return len(self.pre)


def statement(tokens):
    print("in statement")
    tokens = TokenGenerator(tokens)
    while True:
        try:
            res = e_obj(tokens)
            for i in res:
                yield i
        except NoneOfMyBusiness:
            for i in range(len(tokens)):
                yield tokens[i]
            tokens.clear()
        except StopIteration:
            return None


def e_obj(tokens):
    first = tokens[0]
    if first.type == tokenize.NAME:
        if first.value == "e":
            second = tokens[1]
            if second.type != tokenize.STRING and second - first != (0, 1):
                raise NoneOfMyBusiness()
            tokens.clear()  # 清空两个缓存
            return (
                Token(tokenize.NAME, "Exec", start=first.start),
                Token(tokenize.OP, '('),
                Token(tokenize.STRING, second.value),
                Token(tokenize.OP, ')', end=second.end)
            )
        if first.value == 'g':
            second = tokens[1]
            if second.type != tokenize.STRING and second - first != (0, 1):
                raise NoneOfMyBusiness()
            tokens.clear()  # 清空两个缓存
            return (
                Token(tokenize.NAME, "Filter", start=first.start),
                Token(tokenize.OP, '('),
                Token(tokenize.STRING, second.value),
                Token(tokenize.OP, ')', end=second.end)
            )
    raise NoneOfMyBusiness
