"""Validation driver for MDD4REST__mdd4rest-annotator__server_src_rdflib2_plugins_sparql_results_rdfresults.py__RDFResult___init__.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).

`graph.value(predicate=RDF.type, object=RS.ResultSet)` (no subject given)
returns an arbitrary first match, so a single fixture graph cannot safely
hold more than one `a rs:ResultSet` subject -- which of the SELECT/ASK/
CONSTRUCT branches actually runs would become nondeterministic. Each branch
therefore gets its own graph: `fixture.ttl` (SELECT -- several solutions of
every joined pattern, the zero-solution case for the inner binding join, and
neighbouring triples that must not match; see that file's own header) plus
three small inline graphs (ASK true, ASK false, CONSTRUCT/no-ResultSet-at-all
-- the zero-solution case for the outer `m{ }.first()` itself).

`entry` is the `run` harness both files carry identically (see meta.json):
the region is a bare `__init__(self, source, **kwargs)` body extracted from
a class, so `run` supplies a throwaway `self` and returns a plain dict of
the attributes it sets, which the harness's structural (dict/list/set)
comparison can walk into -- solution order is not part of this region's
meaning (`ordered=False`).

Calls and fixture triples added by the repair of 2026-10-30 (triage:
equivalence-doubt and weak-oracle), each aimed at a case the first four
calls did not reach:

* fixture.ttl gained ex:sol4, a binding with rs:variable but no rs:value:
  the original stores `{x: None}` (graph.value gives None). It also gained
  neighbours sharing two terms of a pattern (see its last section), so that
  widening a bound term of `{rs} rs:solution ?s`, `{s} rs:binding ?b` or
  `?rs rdf:type rs:ResultSet` into a variable changes the result.
* MULTI_VALUE: a binding with TWO rs:value. The original reads one of them
  with graph.value; a joined `?b rs:variable ?var . ?b rs:value ?val`
  iterates both rows and keeps whichever comes last.
* NO_VARIABLE: a binding with rs:value but no rs:variable. The original
  raises TypeError on `Variable(None)`; both sides must raise the same.
* ASK_UNKNOWN_DATATYPE: an rs:boolean whose literal has no Python value
  (unknown datatype), so `askAnswer.value == None` and both sides must
  raise "Malformed boolean in ask answer!".
* a text stream instead of a Graph: the region's non-Graph branch. It
  calls `graph.load(source)`, which rdflib 7.2.1 no longer has, so both
  sides must raise the same AttributeError -- the call proves the branch is
  taken identically, nothing more.
"""
from io import StringIO
from rdflib import Graph

from rdfeval.harness import run_pair, fixture_graph

FIXTURE = "fixture.ttl"

ASK_TRUE = """
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
@prefix ex: <http://example.org/> .
ex:rsAskTrue a rs:ResultSet ;
    rs:boolean true .
"""

ASK_FALSE = """
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
@prefix ex: <http://example.org/> .
ex:rsAskFalse a rs:ResultSet ;
    rs:boolean false .
"""

# CONSTRUCT: no rs:ResultSet-typed subject anywhere -- the region's own
# zero-solution branch (`rs is None`) -- plus a couple of ordinary triples
# so `self.graph` (a copy of the whole input graph) is non-trivial to
# compare.
CONSTRUCT_DATA = """
@prefix ex: <http://example.org/> .
ex:alice ex:knows ex:bob .
ex:bob ex:knows ex:carol .
"""

MULTI_VALUE = """
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
@prefix ex: <http://example.org/> .
ex:rsMulti a rs:ResultSet ;
    rs:resultVariable "x" ;
    rs:solution ex:solM .
ex:solM rs:binding ex:bM .
ex:bM rs:variable "x" ; rs:value ex:first, ex:second .
"""

NO_VARIABLE = """
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
@prefix ex: <http://example.org/> .
ex:rsNoVar a rs:ResultSet ;
    rs:resultVariable "x" ;
    rs:solution ex:solN .
ex:solN rs:binding ex:bN .
ex:bN rs:value "orphan value" .
"""

ASK_UNKNOWN_DATATYPE = """
@prefix rs: <http://www.w3.org/2001/sw/DataAccess/tests/result-set#> .
@prefix ex: <http://example.org/> .
ex:rsAskBad a rs:ResultSet ;
    rs:boolean "maybe"^^ex:unknownDatatype .
"""


def _select():
    return ((fixture_graph(FIXTURE),), {})


def _from_text(text):
    return lambda: ((Graph().parse(data=text, format="turtle"),), {})


VERDICT = run_pair(
    __file__,
    entry="run",
    ordered=False,
    calls=[
        _select,
        _from_text(ASK_TRUE),
        _from_text(ASK_FALSE),
        _from_text(CONSTRUCT_DATA),
        _from_text(MULTI_VALUE),
        _from_text(NO_VARIABLE),
        _from_text(ASK_UNKNOWN_DATATYPE),
        lambda: ((StringIO(ASK_TRUE),), {}),
    ],
)
