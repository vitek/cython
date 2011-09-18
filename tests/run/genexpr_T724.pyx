# mode: run
# ticket: 724
# tags: genexpr

def t724():
    """
    >>> t724()
    [[1, 2, 3], [4, 5, 6]]
    """
    return [list(k) for k in
            [(j for j in i)
             for i in [(1,2,3), (4, 5, 6)]]]

## def t724_char_ptr():
##     """
##     >>> ''.join(t724_char_ptr())
##     'Hello, world!'
##     """
##     cdef char *s = "Hello, world!"
##     return (c for c in s)
