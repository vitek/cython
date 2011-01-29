# Unreachable code

def simple_return():
    return
    print 'Where am I?'

def simple_loops(*args):
    for i in args:
        continue
        print 'Never be here'

    while True:
        break
        print 'Never be here'

def conditional(a, b):
    if a:
        return 1
    elif b:
        return 2
    else:
        return 3
    print 'oops'

_ERRORS = """
5:4: Unreachable code
10:8: Unreachable code
14:8: Unreachable code
23:4: Unreachable code
"""
