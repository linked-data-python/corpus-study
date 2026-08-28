"""Context shim for this example, imported identically by both sides.

`CompValue` is copied from MKLab-ITI/prophet@eee2ab51de
rdflib/plugins/sparql/parserutils.py (lines 136-176).  That module cannot be
imported as it stands: the rdflib vendored in that repository is Python 2
(`except SPARQLError, e` a few lines below, `rdflib.py3compat`), so only the
one class the region needs is reproduced here, verbatim except for
`OrderedDict` now coming from the standard library.

`_value` still refers to the module's `value()` helper; it is unreachable
here because `ctx` is never set on the parse values this region sees (the
`__getattr__` fallback returns None for it), which is exactly the situation
in `Prologue.absolutize`.
"""
from collections import OrderedDict


class CompValue(OrderedDict):

    """
    The result of parsing a Comp
    Any included Params are avaiable as Dict keys
    or as attributes

    """

    def __init__(self, name, **values):
        OrderedDict.__init__(self)
        self.name = name
        self.update(values)

    def __str__(self):
        return self.name + "_" + OrderedDict.__str__(self)

    def __repr__(self):
        return self.name + "_" + dict.__repr__(self)

    def _value(self, val, variables=False, errors=False):
        if self.ctx is not None:
            return value(self.ctx, val, variables)  # noqa: F821 - unreachable here
        else:
            return val

    def __getitem__(self, a):
        return self._value(OrderedDict.__getitem__(self, a))

    def get(self, a, variables=False, errors=False):
        return self._value(OrderedDict.get(self, a, a), variables, errors)

    def __getattr__(self, a):
        # Hack hack: OrderedDict relies on this
        if a in ('_OrderedDict__root', '_OrderedDict__end'):
            raise AttributeError
        try:
            return self[a]
        except KeyError:
            # raise AttributeError('no such attribute '+a)
            return None
