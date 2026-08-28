"""Validation driver: Prologue.__init__ sets up a namespace manager.

The region is a plain method body, so the driver supplies a bare stand-in
``self``.  Its ``__eq__`` compares the two observable effects of the region:
the ``base`` attribute and the prefix bindings held by the created
``NamespaceManager``.
"""
from rdfeval.harness import run_pair


class _Prologue:
    """Stand-in for the SPARQL ``Prologue`` instance being initialised."""

    def __eq__(self, other):
        if not isinstance(other, _Prologue):
            return NotImplemented
        return (
            self.__dict__.keys() == other.__dict__.keys()
            and self.base == other.base
            and sorted(self.namespace_manager.namespaces())
            == sorted(other.namespace_manager.namespaces())
        )


def bare_prologue():
    return ((_Prologue(),), {})


VERDICT = run_pair(__file__, entry="__init__", calls=[bare_prologue])
