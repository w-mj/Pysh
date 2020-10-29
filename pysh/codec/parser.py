# token: type, value, (start), (end), line
import tokenize
from .excepts import NoneOfMyBusiness
from .token import Token, TokenGenerator, TokenList, temp_name


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


def statement(tokens: TokenGenerator, not_first=False):
    o1 = e_obj(tokens, not_first)
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
        elif f1.value == '=':
            op = f1
            tokens.clear()
    if op:
        try:
            o2 = statement(tokens, o1.type != TokenList.Normal)
        except NoneOfMyBusiness:
            tokens.push_front(op)
            tokens.push_front(o1)
            raise NoneOfMyBusiness

        if o1.type == TokenList.Normal and o2.type == TokenList.Normal:
            tokens.push_front(o2)
            tokens.push_front(op)
            tokens.push_front(o1)
            raise NoneOfMyBusiness

        if o1.generated_name:
            o1.push_front([
                Token(tokenize.NAME, o1.var_name),
                Token(tokenize.OP, '=')
            ])

        o1.eol()  # o1为赋值语句，换一行
        if not o2.have_name or o2.generated_name:
            o2.newline().push_front([
                Token(tokenize.NAME, o2.var_name),
                Token(tokenize.OP, '=')
            ])  # o2添加赋值语句
        o2.newline().eol()
        tk_func = None
        if op.value == '|':
            tk_func = Token(tokenize.NAME, 'set_input')
        elif op.value == '||':
            tk_func = Token(tokenize.NAME, 'run_if_not_success')
        elif op.value == '&&':
            tk_func = Token(tokenize.NAME, 'run_if_success')
        elif op.value == '=':
            pass
        else:
            raise RuntimeError("Not supported operator " + op.value)
        if tk_func:
            # 处理其他符号
            o3 = TokenList([
                Token(tokenize.NAME, o2.var_name),
                Token(tokenize.OP, '.'),
                tk_func,
                Token(tokenize.OP, '('),
                Token(tokenize.NAME, o1.var_name),
                Token(tokenize.OP, ')')
            ], o1.indent, TokenList.FULL).newline()  # o3为将运算符转换成函数语句
            # if not o1.generated_name:
            #
            #     ot.indent = o1.indent
            #     o1 = ot
            o1.push_line(o2).push_line(o3)
            o1.last_var_name = o2.last_var_name
        else:
            # 处理等号
            o3 = TokenList([
                Token(tokenize.NAME, o1.var_name),
                op,
                Token(tokenize.NAME, o2.last_var_name)
            ], o1.indent, TokenList.FULL).newline().eol()
            o2.push_line(o3)
            o1 = o2
    return o1


def e_obj(tokens, not_first=False):
    first = tokens[0]
    if first.type == tokenize.NAME:
        second = tokens[1]
        if second.type == tokenize.STRING and second.start == first.end:
            # 是字符串前缀
            tk_func = None
            if first.value == "e":
                tk_func = Token(tokenize.NAME, "Exec", start=first.start)
                second.value = 'f' + second.value
            elif first.value == 'g':
                tk_func = Token(tokenize.NAME, "Filter", start=first.start)
            if tk_func:
                tokens.clear()
                tk = TokenList([
                    tk_func,
                    Token(tokenize.OP, '('),
                    Token(tokenize.STRING, second.value),
                    Token(tokenize.OP, ')', end=second.end)
                ], tokens.indent, TokenList.Exec)
                # tk.indent = tokens.indent
                return tk
            # 是其他的字符串前缀
        else:
            tokens.keep_last_one()
            if not_first:
                # 不是第一次出现的普通符号，作为制作一个函数闭包
                tk = TokenList([
                    Token(tokenize.NAME, "FuncFilter"),
                    Token(tokenize.OP, '('),
                    Token(tokenize.STRING, first.value),
                    Token(tokenize.OP, ')')
                ], tokens.indent, TokenList.Filter)
                return tk
            else:
                tk = TokenList([first], tokens.indent, TokenList.Normal)
                tk.var_name = first.value
                return tk

    raise NoneOfMyBusiness
