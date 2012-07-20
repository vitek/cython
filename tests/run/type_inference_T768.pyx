# mode: run
# ticket: 768
from cython cimport typeof

def type_inference_del_int():
    """
    >>> type_inference_del_int()
    'Python object'
    """
    try:
        x = 1
        return typeof(x)
    finally:
        del x

def type_inference_del_dict():
    """
    >>> type_inference_del_dict()
    'dict object'
    """
    try:
        x = {}
        return typeof(x)
    finally:
        del x
