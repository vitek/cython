# cython: language_level=2, warn.maybe_uninitialized=True

def list_comp(a):
    r = [i for i in a]
    return i

# dict comp is py3 feuture and don't leak here
def dict_comp(a):
    r = {i: j for i, j in a}
    return i, j

def dict_comp2(a):
    r = {i: j for i, j in a}
    print i, j
    i, j = 0, 0


_ERRORS = """
5:12: 'i' might be used uninitialized
10:12: undeclared name not builtin: i
10:15: undeclared name not builtin: j
14:11: 'i' is used uninitialized
14:14: 'j' is used uninitialized
"""
