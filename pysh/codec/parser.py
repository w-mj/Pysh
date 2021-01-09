from .excepts import NoneOfMyBusiness
from .parser2 import start as st2

def start(tokens):
    ops = [st2]
    sss = 0
    while True:
        for i in range(len(ops)):
            op = ops[i]
            try:
                res = op(tokens)
                sss = 0
                for i in res:
                    yield i
            except NoneOfMyBusiness:
                sss += 1
                if sss == len(ops):
                    for i in range(len(tokens)):
                        yield tokens[i]
                    tokens.clear()
                    sss = 0
                else:
                    continue
                # if i < len(ops) - 1:
                #     continue
                # for i in range(len(tokens)):
                #     yield tokens[i]
                # tokens.clear()
            except StopIteration:
                return None

