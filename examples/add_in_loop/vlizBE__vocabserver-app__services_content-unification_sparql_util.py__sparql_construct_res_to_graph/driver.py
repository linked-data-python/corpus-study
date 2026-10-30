"""Validation driver for vlizBE__vocabserver-app__services_content-unification_sparql_util.py__sparql_construct_res_to_graph.

Establishes semantic equivalence of original.py and translated.ldpy.

The region turns a SPARQL JSON result (s, p, o bindings) into a fresh
graph, which it returns: the returned graph is compared by isomorphism.
In the repository the input is what query_sudo returns from the triple
store (content-unification/web.py:159-165, remove_vocab.py:91-94), and the
graph only goes through serialize_graph_to_sparql, which reads its triples
and not its prefix bindings (sparql_util.py:18-29).

Calls, and what each exercises:

  0 nominal -- an IRI object, a language literal under 'xml:lang', a typed
    literal, a plain literal, two subjects.
  1 edge values (repair of 2026-10-30) -- objects whose RDF term is FALSY
    in rdflib: the empty plain literal "", "0"^^xsd:integer and
    "false"^^xsd:boolean; a language tag under the CONSTRUCT key 'lang';
    the 'typed-literal' and 'bnode' types some stores emit (json_to_term
    makes both a Literal); the same triple twice.  Without this call, a
    truthiness guard `if o: +{ ... }` stayed green: no object of call 0 is
    falsy.
  2 zero bindings -- an empty result: an empty graph.
"""
from rdfeval.harness import run_pair

EX = "http://example.org/"
XSD = "http://www.w3.org/2001/XMLSchema#"


def _make_res():
    return {
        "results": {
            "bindings": [
                {
                    "s": {"type": "uri", "value": EX + "a"},
                    "p": {"type": "uri", "value": EX + "p"},
                    "o": {"type": "uri", "value": EX + "b"},
                },
                {
                    "s": {"type": "uri", "value": EX + "a"},
                    "p": {"type": "uri", "value": EX + "label"},
                    "o": {"type": "literal", "value": "hello", "xml:lang": "en"},
                },
                {
                    "s": {"type": "uri", "value": EX + "a"},
                    "p": {"type": "uri", "value": EX + "count"},
                    "o": {"type": "literal", "value": "3",
                          "datatype": "http://www.w3.org/2001/XMLSchema#integer"},
                },
                {
                    "s": {"type": "uri", "value": EX + "c"},
                    "p": {"type": "uri", "value": EX + "plain"},
                    "o": {"type": "literal", "value": "plain text"},
                },
            ]
        }
    }


def _row(s, p, o):
    return {"s": {"type": "uri", "value": EX + s},
            "p": {"type": "uri", "value": EX + p}, "o": o}


def _make_edge_res():
    return {
        "results": {
            "bindings": [
                _row("d", "empty", {"type": "literal", "value": ""}),
                _row("d", "zero", {"type": "literal", "value": "0",
                                   "datatype": XSD + "integer"}),
                _row("d", "flag", {"type": "typed-literal", "value": "false",
                                   "datatype": XSD + "boolean"}),
                _row("d", "label", {"type": "literal", "value": "bonjour",
                                    "lang": "fr"}),
                _row("d", "node", {"type": "bnode", "value": "b0"}),
                _row("d", "p", {"type": "uri", "value": EX + "e"}),
                _row("d", "p", {"type": "uri", "value": EX + "e"}),
            ]
        }
    }


def _make_empty_res():
    return {"results": {"bindings": []}}


VERDICT = run_pair(
    __file__,
    entry='sparql_construct_res_to_graph',
    calls=[
        lambda: ((_make_res(),), {}),
        lambda: ((_make_edge_res(),), {}),
        lambda: ((_make_empty_res(),), {}),
    ],
)
