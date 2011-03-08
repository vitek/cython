# cython: warn.maybe_uninitialized=True

def foo(x):
    a = 1
    del a, b
    b = 2
    return a, b

_ERRORS = """
5:9: Deletion of non-Python, non-C++ object
5:12: local variable 'b' referenced before assignment
5:12: Deletion of non-Python, non-C++ object
7:12: local variable 'a' referenced before assignment
"""
