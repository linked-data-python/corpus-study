"""Validation driver for dtai-kg__SCOOP__SCOOP_shape_integration_priority.py__ShapeIntegrationPriority___init__.

`__init__` is an unbound method extracted as a plain function: `self` must
be supplied explicitly.  A minimal stand-in with value-based equality lets
the harness compare the attributes the constructor sets, the same way it
would compare a dataclass instance.

`self.random_number` is `[random.randint(1000, 9999) for _ in range(1000)]`
— a fresh draw every call, on both sides, from whatever state the shared
`random` module happens to be in.  Nothing in the region reads this list
back into RDF; it is excluded from the equality check on purpose (comparing
its 1000 values would fail on non-determinism that has nothing to do with
the translation).
"""
from rdflib import Graph

from rdfeval.harness import run_pair, graphs_isomorphic


class _Self:
    """Stand-in for the real object `__init__` is called on."""

    def __eq__(self, other):
        if not isinstance(other, _Self):
            return NotImplemented
        keys = (set(vars(self)) | set(vars(other))) - {"random_number"}
        for k in keys:
            a, b = getattr(self, k, None), getattr(other, k, None)
            if isinstance(a, Graph) and isinstance(b, Graph):
                if not graphs_isomorphic(a, b):
                    return False
            elif a != b:
                return False
        return True

    def __repr__(self):
        return f"_Self({ {k: v for k, v in vars(self).items() if k != 'random_number'} !r})"


VERDICT = run_pair(
    __file__,
    entry='__init__',
    calls=[
        lambda: ((_Self(), ["shape1", "shape2"], "output.ttl"), {}),
        lambda: ((_Self(), [], ""), {}),
    ],
)
