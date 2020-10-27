# token: type, value, (start), (end), line
import tokenize
from .excepts import NoneOfMyBusiness
from .token import Token, TokenGenerator, TokenList


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
        o1.push_front([
            Token(tokenize.NAME, o1.var_name),
            Token(tokenize.OP, '=')
        ]).eol()
        if not o2.have_name:
            o2.newline().push_front([
                Token(tokenize.NAME, o2.var_name),
                Token(tokenize.OP, '=')
            ]).eol()
        else:
            o2.newline()
        o3 = TokenList(
            Token(tokenize.NAME, o2.var_name),
            Token(tokenize.OP, '.'),
            Token(tokenize.NAME, 'set_input'),
            Token(tokenize.OP, '('),
            Token(tokenize.NAME, o1.var_name),
            Token(tokenize.OP, ')')
        ).newline().eol()
        print(o1.indent)
        o1.push_line(o2, o1.indent).push_line(o3, o1.indent)
        # o1.push_line(o2, 0).push_line(o3, 0)
    return o1


def e_obj(tokens):
    first = tokens[0]
    if first.type == tokenize.NAME:
        if first.value == "e":
            tk_func = Token(tokenize.NAME, "Exec", start=first.start)
        elif first.value == 'g':
            tk_func = Token(tokenize.NAME, "Filter", start=first.start)
        else:
            raise NoneOfMyBusiness()
        second = tokens[1]
        if second.type != tokenize.STRING or second.start != first.end:
            raise NoneOfMyBusiness()
        tokens.clear()  # 清空两个缓存
        tk = TokenList(
            tk_func,
            Token(tokenize.OP, '('),
            Token(tokenize.STRING, second.value),
            Token(tokenize.OP, ')', end=second.end)
        )
        tk.indent = tokens.indent
        return tk
    raise NoneOfMyBusiness
