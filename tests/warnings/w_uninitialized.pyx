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

_ERRORS = """
2:11: Variable 'a' is used uninitialized
8:12: Variable 'a' may be used uninitialized
"""
