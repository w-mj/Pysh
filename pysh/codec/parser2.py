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
        assigned_name = None
        if assignment != -1:
            assert assignment == 1
            assigned_name = self._line[0]
        self._cur = assignment + 1
        tk = TokenList([], self._line.indent)
        stat_token_list = self.generate_statement()
        tk.push_line(stat_token_list)
        tk.var_name = stat_token_list.var_name
        tk.last_var_name = stat_token_list.last_var_name
        if assignment != -1:
            # tk.push_back(self.generate_assignment(assigned_name.value, tk.last_var_name))
            stat_token_list.push_back(self.generate_assignment(assigned_name.value, stat_token_list.last_var_name))
        return stat_token_list

    def generate_assignment(self, assigned_name: str, name: str) -> TokenList:
        return TokenList([
            Token(tokenize.NAME, assigned_name),
            Token(tokenize.OP, '='),
            Token(tokenize.NAME, name)
        ], self._line.indent).eol()

    G_STR = 1
    E_STR = 2
    NAME = 3
    B_STR = 4

    def extract_e_obj(self) -> Tuple[int, int]:
        i = self._cur
        t = -1
        if self._line[i].type == tokenize.NAME and self._line[i].value == 'e' and \
                self._line[i + 1].type == tokenize.STRING:
            self._cur += 2
            return self.E_STR, i + 1
        elif self._line[i].type == tokenize.NAME and self._line[i].value == 'g' and \
                self._line[i + 1].type == tokenize.STRING:
            self._cur += 2
            return self.G_STR, i + 1
        elif self._line[i].type == tokenize.ERRORTOKEN and self._line[i].value == '`':
            assert self._line[i + 1].type == tokenize.NAME
            assert self._line[i + 2].type == tokenize.ERRORTOKEN and self._line[i + 2].value == '`'
            self._cur += 3
            return self.B_STR, i + 1
        elif self._line[i].type == tokenize.NAME:
            self._cur += 1
            return self.NAME, i
        elif self._line[i].type == tokenize.STRING:
            self._cur += 1
            return self.G_STR, i
        return -1, -1

    PIPE = 0
    AND = 1
    OR = 2
    STREAM = 3

    def extract_operator(self) -> int:
        i = self._cur
        if self._line[i].type == tokenize.OP and self._line[i].value == '|':
            self._cur += 1
            if self._line[i + 1].type == tokenize.OP and self._line[i + 1].value == '|':
                self._cur += 1
                return self.OR
            else:
                return self.PIPE
        if self._line[i].type == tokenize.OP and self._line[i].value == '&':
            if self._line[i + 1].type == tokenize.OP and self._line[i + 1].value == '&':
                self._cur += 2
                return self.AND
            return -1
        if self._line[i].type == tokenize.OP and self._line[i].value == '~':
            self._cur += 1
            return self.STREAM
        return -1

    def generate_token_list(self, obj_type: int, pos: int) -> TokenList:
        if obj_type == self.E_STR:
            tk = Token(tokenize.NAME, 'Exec')
            self._line[pos].value = self.generate_cmd_str(self._line[pos].value)
        elif obj_type == self.G_STR:
            tk = Token(tokenize.NAME, 'Filter')
        elif obj_type == self.NAME:
            tk = Token(tokenize.NAME, 'PackName')
        else:
            raise RuntimeError("??")
        tk = TokenList([
            tk,
            Token(tokenize.OP, '(', end=self._line[pos].start),
            self._line[pos],
            Token(tokenize.OP, ')')
        ], self._line.indent)
        tk.push_front(([Token(tokenize.NAME, tk.var_name), Token(tokenize.OP, '=')]))
        tk.last_var_name = tk.var_name
        tk.eol()
        return tk

    def generate_operator_function(self, name1: str, name2: str, op: int) -> TokenList:
        if op == self.PIPE:
            tk = Token(tokenize.NAME, 'set_input')
        elif op == self.AND:
            tk = Token(tokenize.NAME, 'run_if_success')
        elif op == self.OR:
            tk = Token(tokenize.NAME, 'run_if_not_success')
        elif op == self.STREAM:
            tk = Token(tokenize.NAME, 'set_stream_input')
        else:
            raise RuntimeError('???????')
        return TokenList([
            Token(tokenize.NAME, name2),
            Token(tokenize.OP, '.'),
            tk,
            Token(tokenize.OP, '('),
            Token(tokenize.NAME, name1),
            Token(tokenize.OP, ')')
        ], self._line.indent).eol()

    def generate_statement(self) -> TokenList:
        obj_type, pos = self.extract_e_obj()
        assert obj_type in (self.G_STR, self.E_STR, self.NAME)
        op = self.extract_operator()
        if op == -1:
            return self.generate_token_list(obj_type, pos)
        o_list_2 = self.generate_statement()
        o_list_1 = self.generate_token_list(obj_type, pos)
        o_list_op = self.generate_operator_function(o_list_1.var_name, o_list_2.var_name, op)
        o_list_1.push_line(o_list_2).push_line(o_list_op)
        o_list_1.last_var_name = o_list_2.last_var_name
        return o_list_1

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


