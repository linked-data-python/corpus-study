"""Validation driver for Query.get_coded_properties.

The region is a method of pyLODE's ``Query``; the only thing it reads from
``self`` is ``self.db``, a Dataset of profile graphs.  The stub below holds
such a Dataset (built from Turtle, one named graph per profile) and its
``__eq__`` also checks that the region left the dataset untouched.

Fixtures: a property that is a qb:CodedProperty in one profile graph (with
rdfs:range and two qb:codeList values), the same dataset with a property
that is *not* coded (the ``if _graphs`` branch is skipped), and a property
declared as coded in two profile graphs at once.
"""
from rdflib import Dataset, URIRef

from rdfeval.harness import run_pair

PROFILE_A = """
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .

<http://example.org/prop/status> a qb:CodedProperty ;
    rdfs:label "Status" ;
    skos:definition "The status of the parcel." ;
    rdfs:range <http://example.org/class/StatusType> ;
    qb:codeList <http://example.org/codelist/status> ,
                <http://example.org/codelist/legacy-status> .

<http://example.org/codelist/status> rdfs:label "Status codelist" ;
    skos:definition "Codes for the status of a parcel." .

<http://example.org/codelist/legacy-status> rdfs:label "Legacy status codelist" .

<http://example.org/class/StatusType> rdfs:label "Status type" .
<http://example.org/class/SurveyedStatusType> rdfs:subClassOf
    <http://example.org/class/StatusType> ; rdfs:label "Surveyed status type" .

<http://example.org/profile/a> rdfs:label "Profile A" .
<http://example.org/class/Parcel> rdfs:label "Parcel" .

<http://example.org/prop/plain> rdfs:label "Plain property" .
"""

PROFILE_B = """
@prefix qb:   <http://purl.org/linked-data/cube#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

<http://example.org/prop/status> a qb:CodedProperty ;
    rdfs:label "Statut" ;
    rdfs:range <http://example.org/class/StatusType> ;
    qb:codeList <http://example.org/codelist/status> .

<http://example.org/profile/b> rdfs:label "Profile B" .
"""

CLS = URIRef("http://example.org/class/Parcel")
CODED = URIRef("http://example.org/prop/status")
PLAIN = URIRef("http://example.org/prop/plain")


def build_db(graphs):
    db = Dataset(default_union=True)
    for iri, data in graphs:
        db.graph(URIRef(iri)).parse(data=data, format="turtle")
    return db


class _Query:
    """Stand-in for pyLODE's Query (the region's ``self``)."""

    def __init__(self, graphs):
        self.db = build_db(graphs)

    def _quads(self):
        return sorted(repr(q) for q in self.db.quads((None, None, None, None)))

    def __eq__(self, other):
        # the region must not modify the dataset
        return isinstance(other, _Query) and self._quads() == other._quads()

    def __repr__(self):
        return "_Query(%d quads)" % len(self._quads())


ONE = [("http://example.org/profile/a", PROFILE_A)]
TWO = [("http://example.org/profile/a", PROFILE_A),
       ("http://example.org/profile/b", PROFILE_B)]


def case(graphs, props):
    return lambda: ((_Query(graphs), CLS, {p: [] for p in props}), {})


VERDICT = run_pair(
    __file__,
    entry="get_coded_properties",
    calls=[
        case(ONE, [CODED]),            # coded in one profile graph
        case(ONE, [PLAIN]),            # not coded -> `if _graphs` skipped
        case(ONE, [CODED, PLAIN]),     # both
        case(TWO, [CODED]),            # coded in two profile graphs
        case(ONE, []),                 # empty property dict
    ],
)
