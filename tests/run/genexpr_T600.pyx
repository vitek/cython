# mode: run
# ticket: 600

def test_genexpr_lookup(*i):
    """
    >>> list(test_genexpr_lookup(1, 2, 3))
    [1, 4, 9]
    """
    return (i * i for i in i)

def test_genexpr_scope():
    """
    >>> list(test_genexpr_scope())
    [1, 2, 3]
    """
    x = [[1, 2, 3]]
    edges = [6,6,6]
    return (edge for edges in x for edge in edges)
