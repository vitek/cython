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
4:12: Variable 'a' may be used uninitialized
10:12: Variable 'a' may be used uninitialized
"""
