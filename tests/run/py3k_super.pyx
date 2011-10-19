# mode: run
# tags: py3k_super

class A(object):
    def method(self):
        return 1

class B(A):
    """
    >>> obj = B()
    >>> obj.method()
    1
    """
    def method(self):
        return super().method()
