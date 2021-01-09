
def check_switch_case_condition(x, a):
    if callable(a):
        return a(x)
    return a == x