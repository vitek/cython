def simple():
    print a
    a = 0

def simple2(arg):
    if arg > 0:
        a = 1
    return a

def simple_pos(arg):
    if arg > 0:
        a = 1
    else:
        a = 0
    return a

def ifelif(c1, c2):
    if c1 == 1:
        if c2:
            a = 1
        else:
            a = 2
    elif c1 == 2:
        a = 3
    return a

_ERRORS = """
2:11: Variable 'a' is used uninitialized
8:12: Variable 'a' may be used uninitialized
25:12: Variable 'a' may be used uninitialized
"""
