"""Validation driver for ExecutionContext._URI (pyRdfa).

The region is a method; it is exercised as a plain function with a duck-typed
`self` (only `.base`, `.parsedBase`, `.options.add_warning` and
`.node.nodeName` are touched).  The fixtures cover every return path:
the empty-value shortcut, the "base is a local file" branch (relative and
absolute value), the urljoin branch including its '#'/'?' corner case, and an
unusual URI scheme, which triggers the warning side effect.
"""
from urllib.parse import urlsplit

from rdfeval.harness import run_pair


class _Options:
    def __init__(self):
        self.warnings = []

    def add_warning(self, msg, node=None):
        self.warnings.append((msg, node))

    def __eq__(self, other):
        return isinstance(other, _Options) and self.warnings == other.warnings


class _Node:
    nodeName = "a"

    def __eq__(self, other):
        return isinstance(other, _Node)


class _Context:
    """Stand-in for pyRdfa's ExecutionContext, as far as _URI needs it."""

    def __init__(self, base):
        self.base = base
        self.parsedBase = urlsplit(base)
        self.options = _Options()
        self.node = _Node()

    def __eq__(self, other):  # the harness compares arguments after the call
        return (isinstance(other, _Context) and self.base == other.base
                and self.options == other.options)


def _call(base, val):
    return lambda: ((_Context(base), val), {})


HTTP = "http://example.org/dir/doc.html"
LOCAL = "/home/user/docs/doc.html"

VERDICT = run_pair(__file__, entry="_URI", calls=[
    _call(HTTP, ""),                      # empty value -> the base itself
    _call(HTTP, "sub/other.html"),        # plain urljoin
    _call(HTTP, "sub/other.html#"),       # '#' swallowed by urljoin
    _call(HTTP, "sub/other.html?"),       # '?' swallowed by urljoin
    _call(HTTP, "http://other.example/x"),
    _call(HTTP, "weird://host/x"),        # unusual scheme -> add_warning
    _call(LOCAL, "rel.html"),             # parsedBase[0] == "" branch
    _call(LOCAL, "http://example.org/a"),  # ... with an absolute value
])
