# Context shim (see meta.json): the region imports from kif_lib's two
# re-export modules, `..rdflib` and `..typing`.  Both are pure re-exports --
# kif_lib/rdflib.py forwards rdflib's names and kif_lib/typing.py forwards
# typing / collections.abc / typing_extensions names -- so this module
# reproduces exactly the bindings the region asks for, from
# IBM/kif@4ce99d0d9b.  Imported identically by both representations.
from collections.abc import Collection
from typing import Final, TypeAlias, Union

from rdflib import URIRef
from rdflib.namespace import DefinedNamespace, Namespace

__all__ = (
    'Collection',
    'DefinedNamespace',
    'Final',
    'Namespace',
    'TypeAlias',
    'URIRef',
    'Union',
)
