def nested_del():
    a = 1
    def x():
        return a
    del a
    return x

## del nested_del_nonlocal():
##     a = 1
##     def x():
##         nonlocal a
##         del a
##     return x

_ERRORS = """
5:9: can not delete variable 'a' referenced in nested scope
"""
