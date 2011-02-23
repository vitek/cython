# cython: warn.maybe_uninitialized=True

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

def nowimpossible(a):
    if a:
        b = 1
    if a:
        print b

def fromclosure():
    def bar():
        print a
    a = 1
    return bar

_ERRORS = """
4:11: 'a' is used uninitialized
10:12: 'a' might be used uninitialized
27:12: 'a' might be used uninitialized
33:15: 'b' might be used uninitialized
"""
