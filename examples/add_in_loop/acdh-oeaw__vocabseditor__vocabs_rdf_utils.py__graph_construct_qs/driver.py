"""Validation driver for acdh-oeaw__vocabseditor__vocabs_rdf_utils.py__graph_construct_qs.

Establishes semantic equivalence of original.py and translated.ldpy.

graph_construct_qs reads `results`, a Django QuerySet of Concept model
instances -- context_shim.py's QuerySetStub/ModelStub duck-type just the
methods this region calls (`.first()`, `.all()`, `.get_subject()`,
`.as_graph()`, `.create_uri()`), since instantiating the real Django models
is out of scope. The function never mutates `results` or anything reached
through it (every graph accumulation is `g = g + ...`, which builds a NEW
Graph rather than mutating an operand), so RESULTS_1/RESULTS_2 below are
each built ONCE in this module and passed as a plain (non-callable)
`(args, kwargs)` -- both sides then receive the SAME Python objects, which
matters here: ModelStub has no `__eq__`, so if each side got its own
independently-built fixture, comparing `results` as a call argument would
report a spurious difference on identity alone (same pitfall as the
JonasHeinickeBio/biomedical-knowledge-lookup region in this corpus, solved
there with a demo() wrapper instead -- here the simpler fix is to not
rebuild the fixture per side in the first place, since nothing mutates it).

RESULTS_1 -- two concepts. CONCEPT_1 has a non-empty `.collection.all()`
with two collections: COLL_1 has both `.creator` and `.contributor` set
(multi-name, semicolon-separated -- exercises the inner `for i in
x.creator.split(';')` sub-loop with more than one item) and two members,
one with `.legacy_id` set (the `if` branch) and one without (the `.create_uri()`
fallback `else` branch); COLL_2 has neither creator/contributor set and an
EMPTY `.has_members.all()` (the whole members block skipped). CONCEPT_2 has
an empty `.collection.all()` (the whole collection block skipped). This
walks every branch and, critically, exercises the repeated `g = g + ...`
reassignment this region makes three separate times (initial union with the
scheme graph, once per concept, once per collection) -- the reason
translated.ldpy re-declares `@graph g` after each one (see meta.json).

RESULTS_2 -- a single concept with no collection at all: the minimal case,
only the scheme graph and the one `skos:inScheme` triple.
"""
from rdfeval.harness import run_pair
from rdflib import Graph, Literal, URIRef
from context_shim import ModelStub, QuerySetStub

SKOS_NS = "http://www.w3.org/2004/02/skos/core#"


def _labelled_graph(subject, label):
    g = Graph()
    g.add((subject, URIRef(SKOS_NS + "prefLabel"), Literal(label)))
    return g


SCHEME = ModelStub(
    subject=URIRef("http://example.org/scheme/main"),
    graph=_labelled_graph(URIRef("http://example.org/scheme/main"), "Main scheme"),
)

MEMBER_1 = ModelStub(legacy_id="http://example.org/legacy/m1")
MEMBER_2 = ModelStub(legacy_id=None, uri="http://example.org/concept/m2")

COLL_1 = ModelStub(
    subject=URIRef("http://example.org/collection/1"),
    graph=_labelled_graph(URIRef("http://example.org/collection/1"), "Collection One"),
    creator="Alice; Bob",
    contributor="Carol",
    has_members=QuerySetStub([MEMBER_1, MEMBER_2]),
)
COLL_2 = ModelStub(
    subject=URIRef("http://example.org/collection/2"),
    graph=Graph(),
    creator="",
    contributor="",
    has_members=QuerySetStub([]),
)

CONCEPT_1 = ModelStub(
    uri="http://example.org/concept/1",
    graph=_labelled_graph(URIRef("http://example.org/concept/1"), "Concept One"),
    scheme=SCHEME,
    collection=QuerySetStub([COLL_1, COLL_2]),
)
CONCEPT_2 = ModelStub(
    uri="http://example.org/concept/2",
    graph=Graph(),
    scheme=SCHEME,
    collection=QuerySetStub([]),
)

RESULTS_1 = QuerySetStub([CONCEPT_1, CONCEPT_2])
RESULTS_2 = QuerySetStub([ModelStub(uri="http://example.org/concept/3", graph=Graph(),
                                     scheme=SCHEME, collection=QuerySetStub([]))])

VERDICT = run_pair(
    __file__,
    entry='graph_construct_qs',
    calls=[
        ((RESULTS_1,), {}),
        ((RESULTS_2,), {}),
    ],
)
