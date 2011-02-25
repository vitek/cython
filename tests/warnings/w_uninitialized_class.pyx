# cython: warn.maybe_uninitialized=True
# class scope

def foo():
    class Foo(object):
        print a
        a = 1
    return Foo

_ERRORS = """
6:14: 'a' is used uninitialized
"""
