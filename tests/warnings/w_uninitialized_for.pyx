# cython: warn.maybe_uninitialized=True

def simple_for(n):
    for i in n:
        a = 1
    return a

def simple_for_break(n):
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

def simple_target(n):
    for i in n:
        pass
    return i

def simple_target_f(n):
    for i in n:
        i *= i
    return i

_ERRORS = """
6:12: local variable 'a' might be referenced before assignment
12:12: local variable 'a' might be referenced before assignment
24:12: local variable 'i' might be referenced before assignment
29:12: local variable 'i' might be referenced before assignment
"""
