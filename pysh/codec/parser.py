# token: type, value, (start), (end), line
import tokenize
from .excepts import NoneOfMyBusiness
from .token import Token, TokenGenerator, TokenList


def _temp_generator():
    i = 0
    while True:
        i += 1
        yield f"_temp_{i}"

temp = _temp_generator()


def start(tokens):
    while True:
        try:
            res = statement(tokens)
            for i in res:
                yield i
        except NoneOfMyBusiness:
            for i in range(len(tokens)):
                yield tokens[i]
            tokens.clear()
        except StopIteration:
            return None


def statement(tokens: TokenGenerator):
    o1 = e_obj(tokens)
    op = None
    f1 = tokens[0]
    if f1.type == tokenize.OP:
        if f1.value == '|':
            f2 = tokens[1]
            if f2.type == tokenize.OP and f2.value == '|':
                op = Token(tokenize.OP, "||")
                tokens.clear()
            else:
                op = f1
                tokens.keep_last_one()
        elif f1.value == '&':
            f2 = tokens[1]
            if f2.type == tokenize.OP and f2.value == '&':
                op = Token(tokenize.OP, "&&")
                tokens.clear()
    if op:
        o2 = statement(tokens)
        o1_n = next(temp)
        o1.push_front([
            Token(tokenize.NAME, o1_n),
            Token(tokenize.OP, '=')
        ]).eol()
        o2_n = next(temp)
        o2.newline().push_front([
            Token(tokenize.NAME, o2_n),
            Token(tokenize.OP, '=')
        ]).eol()
        o3 = TokenList(
            Token(tokenize.NAME, o2_n),
            Token(tokenize.OP, '.'),
            Token(tokenize.NAME, 'set_input'),
            Token(tokenize.OP, '('),
            Token(tokenize.NAME, o1_n),
            Token(tokenize.OP, ')')
        ).newline().eol()
        print(tokens.indent)
        o1.push_line(o2, tokens.indent).push_line(o3, tokens.indent)
        # o1.push_line(o2, 0).push_line(o3, 0)
    return o1


def e_obj(tokens):
    first = tokens[0]
    if first.type == tokenize.NAME:
        if first.value == "e":
            second = tokens[1]
            if second.type != tokenize.STRING and second - first != (0, 1):
                raise NoneOfMyBusiness()
            tokens.clear()  # 清空两个缓存
            return TokenList(
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
            return TokenList(
                Token(tokenize.NAME, "Filter", start=first.start),
                Token(tokenize.OP, '('),
                Token(tokenize.STRING, second.value),
                Token(tokenize.OP, ')', end=second.end)
            )
    raise NoneOfMyBusiness
