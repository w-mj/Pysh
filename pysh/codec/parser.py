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
        elif f1.value == '=':
            op = f1
            tokens.clear()
    if op:
        o2 = statement(tokens)
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
            o3 = TokenList(
                Token(tokenize.NAME, o2.var_name),
                Token(tokenize.OP, '.'),
                tk_func,
                Token(tokenize.OP, '('),
                Token(tokenize.NAME, o1.var_name),
                Token(tokenize.OP, ')')
            ).newline()  # o3为将运算符转换成函数语句
            o1.push_line(o2).push_line(o3)
            o1.last_var_name = o2.last_var_name
        else:
            # 处理等号
            o3 = TokenList(
                Token(tokenize.NAME, o1.var_name),
                op,
                Token(tokenize.NAME, o2.last_var_name)
            ).newline().eol()
            o2.push_line(o3)
            o1 = o2
    return o1


def e_obj(tokens):
    first = tokens[0]
    if first.type == tokenize.NAME:
        # 检查是否为特殊字符串
        if first.value == "e":
            tk_func = Token(tokenize.NAME, "Exec", start=first.start)
        elif first.value == 'g':
            tk_func = Token(tokenize.NAME, "Filter", start=first.start)
        else:
            # 普通符号
            tokens.clear()
            tk = TokenList(first)
            tk.indent = tokens.indent
            tk.var_name = first.value
            return tk
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
