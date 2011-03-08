# cython: warn.maybe_uninitialized=True
# class scope

def foo(c):
    class Foo(object):
        if c > 0:
            b = 1
        print a, b
        a = 1
    return Foo

_ERRORS = """
8:15: local variable 'a' referenced before assignment
8:18: local variable 'b' might be referenced before assignment
"""
