# Extracted from kumagallium/asterism@f0977d4d3a : ingest/tests/test_papers_dataset.py
# region: test_structure_round_trip (lines 121-159, stratum sparql_literal)
# licence of the source repository: see meta.json
#
# Test harness only (see meta.json): test_structure_round_trip() calls
# `_seed_ttl()`, a module-level helper defined elsewhere in the same test
# file that reads datasets/papers/seed/paper.ttl (521 KB, produced by a JATS
# parser) from disk. That file is not part of this region's captured
# context, and restoring it verbatim would dwarf the region it feeds -- so
# `_seed_ttl()` is redefined here to read `fixture.ttl` (this directory),
# the corpus/405 reading oracle's own authored input graph, identically on
# both sides. Same convention as the on-disk-fixture rename already used for
# examples/trav_single_value/BD2KOnFHIR__fhirtordf__.../test_value.
#
# The function itself only asserts and returns None; `demo()` turns a failed
# assertion into a comparable value instead of letting run_pair abort on the
# first raise, same convention as that example. Its `fixture` parameter
# (repair of 2026-10-30) chooses the graph _seed_ttl() reads.
import os

import rdflib

PAPER = "https://kumagallium.github.io/asterism/papers/resource/paper/PMC5951533"


# Harness seam (identical on both sides): which fixture _seed_ttl() reads,
# set by demo() so the driver can vary the input graph.
_FIXTURE = "fixture.ttl"


def _seed_ttl() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, _FIXTURE), encoding="utf-8") as f:
        return f.read()


def test_structure_round_trip() -> None:
    g = rdflib.Graph().parse(data=_seed_ttl(), format="turtle")
    # Downward: paper -> section -> paragraph -> sentence, all via po:contains.
    down = list(g.query("""
        PREFIX po: <http://www.essepuntato.it/2008/12/pattern#>
        PREFIX doco: <http://purl.org/spar/doco/>
        SELECT ?sec ?para ?sent WHERE {
          ?paper po:contains ?sec . ?sec a doco:Section ; po:contains ?para .
          ?para a doco:Paragraph ; po:contains ?sent . ?sent a doco:Sentence .
        } LIMIT 1
        """, initBindings={"paper": rdflib.URIRef(PAPER)}))
    assert down, "no paper -> sec -> para -> sentence containment path"
    sec, para, sent = (str(x) for x in down[0])
    # Upward from the sentence: its paragraph, its section, the paper it was quoted
    # from, and its NIF reference context — both up-links the gate names.
    up = list(g.query("""
        PREFIX po: <http://www.essepuntato.it/2008/12/pattern#>
        PREFIX nif: <http://persistence.uni-leipzig.de/nlp2rdf/ontologies/nif-core#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?para ?sec ?paper ?ctx WHERE {
          ?para po:contains ?sent . ?sec po:contains ?para .
          ?sent prov:wasQuotedFrom ?paper ; nif:referenceContext ?ctx .
        } LIMIT 1
        """, initBindings={"sent": rdflib.URIRef(sent)}))
    assert up, "cannot walk back up from the sentence"
    assert [str(x) for x in up[0]] == [para, sec, PAPER, PAPER + "/fulltext"]


def demo(fixture: str = "fixture.ttl") -> object:
    global _FIXTURE
    _FIXTURE = fixture
    try:
        test_structure_round_trip()
        return "ok"
    except AssertionError as e:
        return ("assertion-failed", str(e))
