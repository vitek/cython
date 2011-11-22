# mode: run
# ticket: 600

def test_genexpr_lookup(*i):
    """
    >>> list(test_genexpr_lookup(1, 2, 3))
    [1, 4, 9]
    """
    return (i * i for i in i)
