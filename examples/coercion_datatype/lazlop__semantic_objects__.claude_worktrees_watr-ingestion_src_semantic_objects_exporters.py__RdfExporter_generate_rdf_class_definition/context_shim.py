# Context shim (see meta.json): subset of
# .claude/worktrees/watr-ingestion/src/semantic_objects/namespaces.py and
# semantic_objects/core.py from lazlop/semantic_objects@243c5efd8c, so the
# region executes outside the package. Identical bindings for both
# representations.
#
# namespaces.py binds these to the real rdflib.namespace constants; PARAM is
# the project's own namespace object.
from typing import Self
from rdflib import Namespace
from rdflib.namespace import RDF, RDFS

PARAM = Namespace("urn:___param___#")
SH = Namespace("http://www.w3.org/ns/shacl#")


def bind_prefixes(graph):
    """No-op stand-in: the region never calls it."""


# core.py: Resource._get_iri() is `cls._ns[cls._name]`. The relation
# descriptors the region reads (`relation._name`, `relation._get_iri()`) have
# the same shape, minimally reproduced here -- not the real dataclass-field
# machinery, which the region never touches.
class _Relation:
    def __init__(self, name):
        self._name = name

    def _get_iri(self):
        return PARAM[self._name]


class _TargetThing:
    """A Resource subclass target: has both __name__ and _get_iri()."""
    __name__ = "TargetThing"
    _name = "TargetThing"
    _ns = PARAM

    @classmethod
    def _get_iri(cls):
        return cls._ns[cls._name]


class _PlainTarget:
    """A target that is a class but not a Resource subclass: has __name__
    but no _get_iri()."""
    __name__ = "PlainTarget"


class _SourceThing:
    """The class RdfExporter.generate_rdf_class_definition is generating a
    shape for. _valid_relations covers the three branches the region
    dispatches on: a relation with no target, one whose target is a Resource
    subclass (has _get_iri), and one whose target is a plain class (has
    __name__ but not _get_iri).

    Added by the repair pass (the first three alone left two branches
    unexercised):
      * a self-referential relation whose target is `typing.Self`, exactly as
        the repo writes it (PhysicalSpace.contains in the generated s223
        entities: `(relations.contains, typing.Self)`); `Self.__name__` is
        'Self' and it has no `_get_iri`, so the region rebinds
        `target_class = cls`, which is read later for `sh:class` and for the
        message;
      * the same relation listed twice with two different targets (the repo's
        `_valid_relations` lists a predicate once per accepted target type,
        and the real method also walks `cls.__mro__`, so a predicate recurs);
        the second occurrence must be skipped by `processed_relations`.
    """
    __name__ = "SourceThing"
    _name = "SourceThing"
    _ns = PARAM
    _valid_relations = [
        (_Relation("hasNothing"), None),
        (_Relation("hasTarget"), _TargetThing),
        (_Relation("hasPlain"), _PlainTarget),
        (_Relation("hasSelf"), Self),
        (_Relation("hasTarget"), _PlainTarget),   # repeated predicate: skipped
        (_Relation("hasSelf"), None),             # repeated predicate: skipped
    ]

    @classmethod
    def _get_iri(cls):
        return cls._ns[cls._name]
