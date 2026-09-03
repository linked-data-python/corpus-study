# Context shim (see meta.json): stand-ins for pydantic_rdf.annotation and
# pydantic_rdf.model. pydantic_rdf is a real third-party package -- not
# installed in the shared study venv (its declared `pydantic>=2.11.3` would
# upgrade a dependency every other region and session shares), and its
# source is not something this shim vendors either (the local corpus/repos
# checkout is gitignored scratch data, not something a region should
# depend on to run). Its deserialisation logic (property-path traversal,
# per-model caching, circular-reference detection) is also not what this
# region exercises: the extracted lines are a handful of `graph.add()`
# calls sharing a subject, all of which run and finish BEFORE
# `Organization.parse_graph(graph, org)` is ever called.
#
# The driver's own equivalence check compares the `graph` argument itself
# (isomorphism, after the call returns) -- settled before parse_graph runs,
# and unaffected by what it computes. These stand-ins exist only so the
# extracted function's class bodies and its own parse_graph(...) call and
# `assert len(...) == 2` lines run to completion, identically, on both
# sides; they do not reimplement pydantic_rdf's actual field-resolution
# behaviour. Identical bindings for both representations.
from dataclasses import dataclass
from typing import Any


@dataclass
class WithPredicate:
    """Verbatim shape of pydantic_rdf.annotation.WithPredicate: this region
    only constructs and stores `.predicate`, never reads it back."""

    predicate: Any


class CircularReferenceError(Exception):
    """Imported by original.py but never raised or caught in this region."""


class UnsupportedFieldTypeError(Exception):
    """Imported by original.py but never raised or caught in this region."""


class _ParsedStub:
    """What parse_graph() hands back: two lists of the length this region's
    own assertions require, independent of graph content -- see the module
    docstring above for why that does not weaken the driver's comparison."""

    all_employees = [object(), object()]
    matrix_managers = [object(), object()]


class BaseRdfModel:
    """Enough of pydantic_rdf.model.BaseRdfModel for the Organization/Person
    class bodies in this region to define without error, and for
    parse_graph to return something the region's own assertions accept."""

    @classmethod
    def model_rebuild(cls) -> None:
        return None

    @classmethod
    def parse_graph(cls, graph, uri):
        return _ParsedStub()
