"""Validation driver for LexMalta/recipes sparql/parser.py, <module>_266.

The region only DEFINES the pyparsing rule DECIMAL and its parse action, which
builds `rdflib.Literal(x[0], datatype=XSD.decimal)` from the matched token.
`demo` (identical on both sides, see original.py / translated.ldpy) runs the
rule on a token and returns the term the action built, so the oracle is value
equality on that term -- lexical form and datatype included -- and a parse
failure is compared as a raise (type and message).

Cases:
* "1.50"     the lexical form is kept ("1.50", not "1.5");
* ".5"       rdflib normalises the lexical form ("0.5"): a translation that
             bound the raw token as an untyped/string literal would differ;
* "01.5"     leading zero dropped by the same normalisation ("1.5");
* "12.0", "0.000"  trailing zeros kept;
* "12", "1e3", "abc", "1.5x"  no match (no dot / trailing junk): raises.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry="demo",
    calls=[((t,), {}) for t in ("1.50", ".5", "01.5", "12.0", "0.000",
                                "12", "1e3", "abc", "1.5x")],
    ordered=True,
)
