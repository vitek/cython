def simple():
    print a
    a = 0

def simple2(arg):
    if arg > 0:
        a = 1
    return a

def simple_while(n):
    while n > 0:
        n -= 1
        a = 0
    return a

def simple_while_break(n):
    while n > 0:
        n -= 1
        break
    else:
        a = 1
    return a

def simple_while_pos(n):
    while n > 0:
        n -= 1
        a = 0
    else:
        a = 1
    return a

def simple_for(n):
    for i in n:
        a = 1
    else:
        a = 0
    return a

def simple_for(n):
    for i in n:
        a = 1
        break
    return a

def simple_for_pos(n):
    for i in n:
        a = 1
    else:
        a = 0
    return a

_ERRORS = """
2:11: Variable 'a' is used uninitialized
8:12: Variable 'a' may be used uninitialized
14:12: Variable 'a' may be used uninitialized
22:12: Variable 'a' may be used uninitialized
43:12: Variable 'a' may be used uninitialized
"""
