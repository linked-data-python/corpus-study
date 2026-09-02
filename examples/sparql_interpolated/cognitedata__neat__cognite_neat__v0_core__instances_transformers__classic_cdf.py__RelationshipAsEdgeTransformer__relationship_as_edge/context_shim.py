# Context shim (see meta.json): stand-in for the receiver
# RelationshipAsEdgeTransformer._relationship_as_edge needs on `self`
# (cognite/neat/_v0/core/_instances/transformers/_classic_cdf.py), and for
# the two helpers the region imports from
# cognite/neat/_v0/core/_utils/rdf_.py and
# cognite/neat/_v0/core/_issues/warnings/_resources.py, so the region
# executes outside the cognite-neat package. Identical bindings for both
# representations.
#
# RelationshipAsEdgeTransformer here carries only what the region reads on
# `self`: `_namespace`, `_NOT_PROPERTIES`, `_predicate` and `_create_edge`,
# copied verbatim from the source class (lines 322-503 of the original
# file). The constructor, the other transformer methods (`transform`,
# `_lookup_entity`, `create_lookup_entity_with_external_id`) and the class
# attributes the region never touches are not reproduced.
#
# `remove_namespace_from_uri` is copied verbatim for the single-URI,
# default-argument case, which is the only one the region calls (the
# sequence overload and non-default `validation`/`special_separator` are
# never exercised here).
#
# `Triple`, `add_triples_in_batch`, `get_namespace` and
# `remove_instance_ids_in_batch` are imported by the region but never
# called or referenced in its body (only `Triple` appears, as a type hint
# inside a `cast(...)`, which is a no-op at run time) -- stand-ins only.
#
# `ResourceNotFoundWarning` only needs to be constructible with the same
# positional arguments and passable to `warnings.warn`; the region never
# inspects its fields, so the real pydantic/dataclass machinery
# (ResourceNeatWarning, Generic[...], NeatIssue base) is not reproduced.
from rdflib import RDF


Triple = tuple  # type-hint stand-in only; the region never constructs one


def remove_namespace_from_uri(URI, *, special_separator="#_", validation="prefix"):
    """Verbatim port (single-URI case) of
    cognite.neat._v0.core._utils.rdf_.remove_namespace_from_uri."""
    if str(URI).lower().startswith("http"):
        sep = special_separator if special_separator in URI else ("#" if "#" in URI else "/")
        return URI.split(sep)[-1]
    return str(URI)


def add_triples_in_batch(*args, **kwargs):  # unused by the region
    raise NotImplementedError("not exercised by this region")


def get_namespace(*args, **kwargs):  # unused by the region
    raise NotImplementedError("not exercised by this region")


def remove_instance_ids_in_batch(*args, **kwargs):  # unused by the region
    raise NotImplementedError("not exercised by this region")


class ResourceNotFoundWarning(UserWarning):
    """Stand-in for
    cognite.neat._v0.core._issues.warnings.ResourceNotFoundWarning: same
    constructor shape, warnable, content not inspected by the region."""

    def __init__(self, identifier, resource_type, referred_by, referred_type):
        self.identifier = identifier
        self.resource_type = resource_type
        self.referred_by = referred_by
        self.referred_type = referred_type
        super().__init__(
            f"{resource_type} {identifier!r} referred by {referred_type} {referred_by!r} not found"
        )


class RelationshipAsEdgeTransformer:
    """Stand-in receiver: only the state and helpers
    `_relationship_as_edge` reads on `self`, copied verbatim from the
    source class."""

    _NOT_PROPERTIES = frozenset(
        {"sourceExternalId", "targetExternalId", "externalId", "sourceType", "targetType"}
    )

    def __init__(self, namespace):
        self._namespace = namespace

    def _predicate(self, target_type):
        return self._namespace[f"relationship{target_type.capitalize()}"]

    def _create_edge(self, objects_by_predicates, external_id, source_id, target_id, predicate, edge_type):
        """Verbatim port of RelationshipAsEdgeTransformer._create_edge."""
        edge_triples = []
        edge_id = self._namespace[external_id]

        edge_triples.append((edge_id, RDF.type, edge_type))
        for prop_name, object_ in objects_by_predicates.items():
            if prop_name in self._NOT_PROPERTIES:
                continue
            edge_triples.append((edge_id, self._namespace[prop_name], object_))

        edge_triples.append((source_id, predicate, edge_id))
        edge_triples.append((edge_id, self._namespace["startNode"], source_id))
        edge_triples.append((edge_id, self._namespace["endNode"], target_id))
        return edge_triples
