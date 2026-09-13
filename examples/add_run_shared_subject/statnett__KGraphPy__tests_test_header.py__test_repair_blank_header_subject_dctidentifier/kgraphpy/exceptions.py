# Context shim (see meta.json): subset of kgraphpy/exceptions.py from
# statnett/KGraphPy@38859be62fdc2fd048e3ad1651bc16f0dcabaf75, so the region
# executes outside the package. Identical bindings for both representations.


class NamespaceEmptyError(Exception):
    """Raised when a namespace has no members."""
