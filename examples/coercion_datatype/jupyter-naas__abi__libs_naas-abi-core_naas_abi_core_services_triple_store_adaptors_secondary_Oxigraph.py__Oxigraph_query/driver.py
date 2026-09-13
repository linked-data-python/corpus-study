"""Validation driver for jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_services_triple_store_adaptors_secondary_Oxigraph.py__Oxigraph_query.

The region became a function `query(response, content_type)` (see the header
comment in original.py / translated.ldpy: the extracted lines were a bare
`if/elif/else` with a `return` in each branch, not runnable outside the
enclosing method).

Two calls exercise the two return paths:

- a SPARQL-results (JSON) response, whose bindings cover all four literal
  branches -- a numeric datatype that parses as int (xsd:integer), one that
  fails to parse as int and falls back to the un-cast Literal (xsd:long), a
  non-numeric datatype (xsd:date), a language-tagged literal, a plain
  literal, plus a URI-typed binding, a bnode-typed binding, and one variable
  entirely absent from the row (-> None) -- and
- a Turtle response, taking the CONSTRUCT/DESCRIBE branch.

`query()`'s SPARQL-results branch returns `iter(results)`, a generator of
ResultRow-like objects; `run_pair`'s `materialise()` walks it into a list of
tuples before comparison, and the Turtle branch's return is a `Graph`
compared by isomorphism -- both handled by `run_pair` without help here.
"""
import json

from rdfeval.harness import run_pair


class _FakeResponse:
    # run_pair also compares call arguments (a region may mutate one), so
    # this needs value equality -- it is never mutated by `query`, but two
    # separate instances (one per side) must still compare equal.
    def __init__(self, text):
        self.text = text

    def __eq__(self, other):
        return isinstance(other, _FakeResponse) and self.text == other.text

    def __repr__(self):
        return f"_FakeResponse({self.text!r})"


def _sparql_results_fixture():
    payload = {
        "head": {"vars": ["s", "int_ok", "int_bad", "date", "label", "plain", "missing"]},
        "results": {
            "bindings": [
                {
                    "s": {"type": "uri", "value": "http://example.org/a"},
                    "int_ok": {
                        "type": "literal",
                        "value": "42",
                        "datatype": "http://www.w3.org/2001/XMLSchema#integer",
                    },
                    "int_bad": {
                        "type": "literal",
                        "value": "not-a-number",
                        "datatype": "http://www.w3.org/2001/XMLSchema#long",
                    },
                    "date": {
                        "type": "literal",
                        "value": "2024-01-01",
                        "datatype": "http://www.w3.org/2001/XMLSchema#date",
                    },
                    "label": {
                        "type": "literal",
                        "value": "bonjour",
                        "xml:lang": "fr",
                    },
                    "plain": {"type": "literal", "value": "hello"},
                    # "missing" is deliberately absent from this binding
                },
                {
                    "s": {"type": "bnode", "value": "b0"},
                    # every other var absent -> None on this row
                },
            ]
        },
    }
    response = _FakeResponse(json.dumps(payload))
    return ((response, "application/sparql-results+json"), {})


def _turtle_fixture():
    ttl = (
        "@prefix ex: <http://example.org/> .\n"
        'ex:a ex:p "hello" .\n'
        "ex:a ex:q ex:b .\n"
    )
    response = _FakeResponse(ttl)
    return ((response, "text/turtle"), {})


VERDICT = run_pair(
    __file__,
    entry="query",
    calls=[_sparql_results_fixture, _turtle_fixture],
)
