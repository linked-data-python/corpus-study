# Context shim (see meta.json): subset of the loader/lookup helpers used by
# landscape/07-tooling/build_core_*.py in
# altunelyusuf/SemanticTechnologies@bad0fa7c46 -- load() returns the
# enrichment layer's item table and its "governs" links, nodes/cls_iri give
# the class-node IRI lookup, bump() is the version-bump side effect on the
# parsed graph, and S(*refs) is the source-citation helper. Reproduced
# minimally so the region executes outside the package; identical bindings
# for both representations.
import os

from rdflib import URIRef

BASEDIR = os.path.join(os.path.dirname(__file__), "fixtures")

nodes = [
    {"id": "role-1"},
    {"id": "activity-1"},
    {"id": "rule-1"},
]


def cls_iri(n):
    return URIRef(f"http://example.org/semtech#{n['id']}")


class _Enrichment:
    ALL_ITEMS = [
        ("role-1", "Role One", "Role", "Definition of role one.", ("R-TOGAF",)),
        ("activity-1", "Activity One", "Activity", "Definition of activity one.", ("R-DAMA", "R-TOGAF")),
        ("rule-1", "Rule One", "Rule", "Definition of rule one.", ("R-DAMA",)),
    ]
    GOVERNS = {"activity-1": "role-1"}


def load(name, version):
    return _Enrichment()


def bump(g):
    return None


def S(*refs):
    return " ".join(refs)
