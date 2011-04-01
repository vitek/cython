# cython: warn.unused=True, warn.unused_arg=True, warn.unused_result=True
def unused_variable():
    a = 1

def unused_cascade(arg):
    a, b = arg.split()
    return a

def unused_arg(arg):
    pass

def unused_result():
    r = 1 + 1
    r = 2
    return r

def unused_nested():
    def unused_one():
        pass

# this should not generate warning
def used(x, y):
    x.y = 1
    y[0] = 1
    lambda x: x

_ERRORS = """
3:6: Unused entry 'a'
6:9: Unused entry 'b'
9:15: Unused argument 'arg'
13:6: Unused result in 'r'
18:4: Unused entry 'unused_one'
"""
