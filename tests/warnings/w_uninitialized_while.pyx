# cython: warn.maybe_uninitialized=True

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

_ERRORS = """
7:12: local variable 'a' might be referenced before assignment
15:12: local variable 'a' might be referenced before assignment
"""
