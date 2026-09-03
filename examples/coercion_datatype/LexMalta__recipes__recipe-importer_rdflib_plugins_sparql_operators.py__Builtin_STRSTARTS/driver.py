"""Validation driver for LexMalta__recipes__recipe-importer_rdflib_plugins_sparql_operators.py__Builtin_STRSTARTS.

`Builtin_STRSTARTS(expr, ctx)` reads `expr.arg1`/`expr.arg2` -- two RDF
`Literal` terms, as rdflib's own SPARQL evaluator supplies them -- and
`ctx`, unused in this 10-line region. `expr` is a plain SimpleNamespace
exposing just `.arg1`/`.arg2` (a real
rdflib.plugins.sparql.parserutils.Expr needs a parsed CompValue to build;
nothing else the region reads justifies constructing one). `ctx=None`
throughout.

CALL_1/2 -- plain-literal arg1/arg2, matching and not matching: exercises
both branches of `str.startswith` and the coercion_datatype site,
`Literal(a.startswith(b))` in original.py vs `f{a.startswith(b)}` in
translated.ldpy -- neither passes a `datatype=`, so both rely on rdflib's
own default inference from a bare Python `bool` (verified separately:
`Literal(True) == Literal('true', datatype=XSD.boolean)`, and `f{ }` goes
through the same `node()` conversion -- see meta.json).

CALL_3 -- both arg1/arg2 language-tagged `@fr`, matching: exercises
`_compatibleStrings`'s language-compatibility check (restored via
context_shim.py) on the way in, without changing the coercion at the
boundary -- the *return* value is a fresh, untagged boolean Literal either
way.
"""
from types import SimpleNamespace

from rdflib import Literal

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='Builtin_STRSTARTS',
    calls=[
        ((SimpleNamespace(arg1=Literal("hello world"), arg2=Literal("hello")), None), {}),
        ((SimpleNamespace(arg1=Literal("hello world"), arg2=Literal("bye")), None), {}),
        ((SimpleNamespace(arg1=Literal("café", lang="fr"), arg2=Literal("caf", lang="fr")), None), {}),
    ],
)
