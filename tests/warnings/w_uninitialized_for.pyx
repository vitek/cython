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

_ERRORS = """
6:12: 'a' might be used uninitialized
12:12: 'a' might be used uninitialized
"""
