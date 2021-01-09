import tokenize
from io import StringIO
import sys
from . import parser

TEXT_TYPE = 'unicode' if sys.version_info[0] == 2 else 'str'


class InterpolationError(tokenize.TokenError): pass


def TK(token, value):
    return tokenize.TokenInfo(token, value, (0, 0), (0, 0), '')


out = open('err.txt', 'w')
def pysh_untokenize(tokens):
    parts = []
    prev_row = 1
    prev_col = 0
    last = None
    indent = 0
    for token in tokens:
        ttype, tvalue, tstart, tend, tline = token.to_token()
        print(token, file=out)
        row, col = tstart

        # if last and last.type in (tokenize.NEWLINE, tokenize.NL):
        #     parts.append('\t' * indent)
        # if ttype == tokenize.INDENT:
        #     indent += 1
        # elif ttype == tokenize.DEDENT:
        #     indent -= 1

        # Add whitespace
        col_offset = col - prev_col
        if col_offset > 0:
            parts.append(" " * col_offset)
            # parts.append(' ')
        # elif last and (last.type, token.type) in (tokenize.NAME, tokenize.NUMBER):
        #     parts.append(' ')

        # if ttype not in (tokenize.INDENT, tokenize.DEDENT):
        parts.append(tvalue)
        prev_row, prev_col = tend

        if ttype in (tokenize.NL, tokenize.NEWLINE):
            prev_row += 1
            prev_col = 0
        if ttype not in (tokenize.INDENT, tokenize.DEDENT):
            last = token
    head = """
from pysh.lib.exec import Exec
from pysh.lib.filter import Filter
from pysh.lib.pack_name import PackName
from pysh.lib.generate_param import generateParam
from pysh.lib.template import check_switch_case_condition

"""
    return head + ''.join(parts)


def get_temp():
    i = 1
    while True:
        yield f"_pysh_temp{i}__"
        i += 1


def indents(n):
    for i in range(n):
        yield tokenize.TokenInfo(tokenize.INDENT, '\t', (0, 0), (0, 0), '')


def pysh_tokenize(readline):
    tokens = tokenize.generate_tokens(readline)
    parse = parser.statement(tokens)
    # print(list(parse))
    return parse
    indent = 0
    last_obj = None
    gen_name = get_temp()
    try:
        while True:
            token = next(tokens)
            print(token)
            ttype, tvalue, tstart, tend, tline = token
            if ttype == tokenize.NAME and tvalue == 'e':
                tnext = next(tokens)
                print(tnext)
                if tnext[0] == tokenize.STRING and tnext[2][1] == tend[1]:
                    # 解析e字符串
                    last_obj = next(gen_name)
                    # yield tokenize.TokenInfo(tokenize.NAME, last_obj, token[2], (0, 0), '')
                    # yield tokenize.TokenInfo(tokenize.OP, '=', (0, 0), (0, 0), '')
                    yield tokenize.TokenInfo(tokenize.NAME, 'Exec', token[2], (0, 0), '')
                    yield tokenize.TokenInfo(tokenize.OP, '(', (0, 0), (0, 0), '')
                    yield tokenize.TokenInfo(tokenize.STRING, tnext[1], (0, 0), (0, 0), '')
                    yield tokenize.TokenInfo(tokenize.OP, ')', (0, 0), tnext[3], '')
                    # yield tokenize.TokenInfo(tokenize.NEWLINE, '\n', (0, 0), tnext[3], '')
                    # for x in indents(indent):
                    #     yield x
                    continue
                else:
                    # e后面不是紧跟字符串，原样返回
                    yield token
                    yield tnext
                    continue
            elif ttype == tokenize.INDENT:
                indent += 1
            elif ttype == tokenize.NEWLINE:
                indent = 0
            yield token
    except (StopIteration, tokenize.TokenError):
        pass
