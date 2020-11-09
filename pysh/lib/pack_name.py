from pysh.lib.exec import Exec, RegexFilter, FuncFilter

def PackName(obj):
    if isinstance(obj, Exec):
        return obj
    if isinstance(obj, str):
        return RegexFilter(obj)
    if callable(obj):
        return FuncFilter(obj)
