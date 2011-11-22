# cython: language_level=3
# mode: run
# ticket: 753

def test_scoped_closure():
    """
    >>> [i() for i in test_scoped_closure()]
    [2, 2, 2]
    """
    return [lambda: i for i in range(3)]


test_VAR = 777
class test_scoped_class_lookup(object):
    """
    >>> test_scoped_class_lookup.var
    [777, 777, 777]
    >>> test_scoped_class_lookup.var2
    [1, 2, 3]
    """
    test_VAR = 123
    var = [test_VAR for i in range(3)]

    class_iterator = [1, 2, 3]
    var2 = [i for i in class_iterator]

def test_scoped_same_name(*i):
    """
    >>> test_scoped_same_name(1, 2, 3)
    [1, 4, 9]
    """
    return [i * i for i in i]

def test_scoped_lookup(*x):
    """
    >>> test_scoped_lookup([1, 2], [3, 4])
    [[1, 2], [3, 4]]
    """
    return [[y for y in i] for i in x]
