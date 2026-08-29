# Context shim (see meta.json): reduced from
# pylode/profiles/supermodel/query/common.py (get_values, get_name) at
# RDFLib/pyLODE@0d0471fb99, so the region executes without installing pylode
# and its own dependencies (pylode.profiles.supermodel.model, a logger).
# Identical bindings for both representations.
from itertools import chain

from rdflib import RDFS, SDO, SKOS, Literal, URIRef


def get_values(iri, graph, properties):
    result = list(chain.from_iterable(graph.objects(iri, prop) for prop in properties))
    for value in result:
        if not isinstance(value, (URIRef, Literal)):
            raise ValueError(
                f"Expected only IRIs or literals but found type {type(value)} "
                f"with value {value} for IRI {iri}"
            )
    return result


def get_name(iri, graph, db=None):
    """Get name for resource: graph first, then db, then a qname fallback."""
    name_predicates = [RDFS.label, SKOS.prefLabel, SDO.name]
    names = get_values(iri, graph, name_predicates)
    if not names and db is not None:
        names = get_values(iri, db, name_predicates)
    if not names:
        try:
            names.append(graph.qname(iri))
        except ValueError:
            pass
    return str(names[0]) if len(names) > 0 else str(iri)
