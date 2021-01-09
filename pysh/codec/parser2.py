import tokenize
from typing import Tuple

from .token import Line, TokenList, Token, TokenGenerator
from .excepts import NoneOfMyBusiness


def start(token: TokenGenerator):
    line = token.get_next_line()
    t = ParseStatement(line).check_e_statement_line()
    token.clear()
    return t


class ParseStatement:
    def __init__(self, line: Line, start: int = 0):
        self._line = line
        self._cur = start

    def check_e_able(self) -> Tuple[bool, int]:
        assignment = -1
        has_e_obj = False
        for i in range(len(self._line)):
            x = self._line[i]
            if x.type == tokenize.OP and x.value == '=':
                if assignment == -1:
                    assignment = True
            if x.type == tokenize.NAME and x.value in ('e', 'g') and self._line[i + 1].type == tokenize.STRING:
                has_e_obj = True
                break
            if x.type == tokenize.ERRORTOKEN and x.value == '`':
                has_e_obj = True
                break
        return has_e_obj, assignment

    def check_e_statement_line(self) -> TokenList:
        has_e_object, assignment = self.check_e_able()
        if not has_e_object:
            raise NoneOfMyBusiness()

        result = []
        i = 0
        back_brackets = 0
        while i < len(self._line):
            x = self._line[i]
            if assignment > 0:
                result.append(x)
                if x.value == '=':
                    assignment = -1
                i += 1
                continue

            tk = None
            if x.type == tokenize.NAME and x.value == 'e' and self._line[i + 1].type == tokenize.STRING:
                self._line[i + 1].value = self.generate_cmd_str(self._line[i + 1].value)
                tk = 'Exec'
            elif x.type == tokenize.NAME and x.value == 'g' and self._line[i + 1].type == tokenize.STRING:
                tk = 'Filter'
            elif x.type == tokenize.NAME:
                tk = 'PackName'
            elif x.type == tokenize.OP and x.value == '|' and \
                    self._line[i + 1].type == tokenize.OP and self._line[i + 1].value == '|':
                tk = '.fail_to'
                i += 1
            elif x.type == tokenize.OP and x.value == '&' and \
                    self._line[i + 1].type == tokenize.OP and self._line[i + 1].value == '&':
                tk = '.success_to'
                i += 1
            elif x.type == tokenize.OP and x.value == '|':
                tk = '.pipe_to'
            elif x.type == tokenize.OP and x.value == '~':
                tk = '.stream_to'

            if tk:
                result += [
                    Token(tokenize.NAME, tk, start=self._line[i].start),
                    Token(tokenize.OP, '(', end=self._line[i + 1].start),
                ]
                if tk == 'PackName':
                    result.append(x)
                    result += [Token(tokenize.OP, ')', end=x.end)] * (back_brackets + 1)
                    back_brackets = 0
                else:
                    back_brackets += 1
            else:
                result.append(x)
                result += [Token(tokenize.OP, ')', end=x.end)] * back_brackets
                back_brackets = 0

            i += 1
        return TokenList(result, indent=self._line.indent)


    def generate_cmd_str(self, cmd: str):
        res = "f"
        state = 1
        for x in cmd:
            if state == 1:
                if x == '$':
                    state = 2
                else:
                    res += x
            elif state == 2:
                if x == '$':
                    state = 1
                    res += x
                elif x == '{':
                    state = 4
                elif str.isdigit(x):
                    state = 1
                    res += f"${x}"
                elif str.isalpha(x) or x == '_':
                    state = 3
                    res += f'{{generateParam({x}'
                else:
                    state = 1
                    res += x
            elif state == 3:
                if str.isalnum(x) or x == '_':
                    res += x
                else:
                    res += f')}}{x}'
                    state = 1
            elif state == 4:
                assert x != '}'
                res += f'{{generateParam({x}'
                state = 5
            elif state == 5:
                if x == '}':
                    state = 1
                    res += ')}'
                else:
                    res += x
        return res
