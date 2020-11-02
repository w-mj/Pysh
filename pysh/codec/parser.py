# token: type, value, (start), (end), line
import tokenize
from typing import List

from .excepts import NoneOfMyBusiness
from .token import Token, TokenGenerator, TokenList, temp_name
from .token import Token, TokenGenerator, TokenList, Line


def start(tokens):
    ops = [statement, check_switch]
    while True:
        for op in ops:
            try:
                res = op(tokens)
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
                tk_func = Token(tokenize.NAME, "RegexFilter", start=first.start)
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


def check_case(line: Line):
    condition: List[Token] = []
    operate: List[Token] = []
    con = True
    for tk in line:
        if con:
            if tk.type == tokenize.OP and tk.value == '->':
                con = False
            else:
                condition.append(tk)
        else:
            operate.append(tk)
    return condition, operate


def generate_case_condition(var, con: List[Token]):
    if con[0].type == tokenize.OP and con[0].value == '==':
        return [var] + con
    if con[0].type == tokenize.OP and con[0].value == '(':
        assert con[4].type == tokenize.OP and con[4].value == ')'
        return [con[1], Token(tokenize.OP, '<'), var, Token(tokenize.OP, '>'), con[3]]
    if con[0].type == tokenize.OP and con[0].value == '[':
        assert con[4].type == tokenize.OP and con[4].value == ']'
        return [con[1], Token(tokenize.OP, '<='), var, Token(tokenize.OP, '>='), con[3]]
    # con[1](var)if callable(con[1])else con[1] == var
    return [
        Token(tokenize.NAME, 'check_switch_case_condition'),
        Token(tokenize.OP, '('),
        var,
        Token(tokenize.OP, ','),
        con[0],
        Token(tokenize.OP, ')')
    ]


def check_switch(tokens: TokenGenerator):
    first = tokens[0]
    if first.type != tokenize.NAME or first.value != 'switch':
        raise NoneOfMyBusiness()
    switch_indent = tokens.indent
    var = tokens[1]
    # switch a:\n
    assert var.type == tokenize.NAME and var.start[0] == first.start[0]
    assert tokens[2].type == tokenize.OP and tokens[2].value == ':'
    assert tokens[3].type == tokenize.NEWLINE
    tokens.clear()
    ans = TokenList([], switch_indent, TokenList.SWITCH)
    while True:
        line = tokens.get_next_line()
        if line.indent == switch_indent + 1:
            # case 语句
            con, ope = check_case(line)
            con = generate_case_condition(var, con)
            ans.push_back([Token(tokenize.NAME, 'if ')] + con + [Token(tokenize.OP, ':'), Token(tokenize.NEWLINE, '\n')])
            ans.push_back(TokenList(ope, switch_indent + 1, TokenList.SWITCH).newline())
            tokens.clear()
            while True:
                line = tokens.get_next_line()
                if line.indent >= switch_indent + 2:
                    # case语句体
                    ans.push_back(TokenList(line, switch_indent + 1, TokenList.SWITCH).newline())
                    tokens.clear()
                else:
                    break
        elif line.indent <= switch_indent:
            break
        else:
            print("????" + str(line.indent))
            break
    return ans.newline()
