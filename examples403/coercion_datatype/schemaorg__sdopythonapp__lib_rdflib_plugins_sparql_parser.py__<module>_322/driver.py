"""Validation driver for schemaorg__sdopythonapp__lib_rdflib_plugins_sparql_parser.py__<module>_322.

The region only DEFINES a pyparsing grammar rule (STRING_LITERAL2) and its
parse action; nothing at module scope is itself an RDF term or a graph, so
there is nothing to compare without running the parser. `demo` (identical on
both sides, see meta.json) parses a concrete SPARQL string-literal token and
returns the rdflib.Literal the parse action built -- the oracle is value
equality on that term (datatype/language included).

Two cases: a token with no escape sequence, and one with an escape (`\\n`,
two characters, not a real newline in the SPARQL source text) that
decodeUnicodeEscape must resolve to an actual newline -- so a translation
that silently dropped the escaping step would be caught.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[
        (('"plain"',), {}),
        (('"hello\\nworld"',), {}),
    ],
)
