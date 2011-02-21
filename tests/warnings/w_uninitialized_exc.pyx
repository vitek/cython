def exc_target():
    try:
        {}['foo']
    except KeyError, e:
        pass
    except IndexError, i:
        pass
    return e, i

def exc_body():
    try:
        a = 1
    except Exception:
        pass
    return a

def exc_else_pos():
    try:
        pass
    except Exception, e:
        pass
    else:
        e = 1
    return e

def exc_body_pos(d):
    try:
        a = d['foo']
    except KeyError:
        a = None
    return a

def exc_pos():
    try:
        a = 1
    except Exception:
        a = 1
    return a

def exc_finally():
    try:
        a = 1
    finally:
        pass
    return a

def exc_finally2():
    try:
        pass
    finally:
        a = 1
    return a

_ERRORS = """
8:12: Variable 'e' may be used uninitialized
8:15: Variable 'i' may be used uninitialized
15:12: Variable 'a' may be used uninitialized
"""
