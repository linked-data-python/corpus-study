"""Validation driver for SynBioDex__sbol_factory__sbol_factory_custom_eval.py__<module>_1.

EXCLUDED (see meta.json), for two independent, stacked reasons -- and the
region's own `if __name__ == "__main__":` guard means run_pair cannot even
reach either of them.

1. `_exec_python`/`_exec_ldpy` (rdfeval.harness) run each file with
   `__name__` set to `"__original__"`/`"__translated__"`, never
   `"__main__"` -- that is how a driver can import a script-shaped region
   without it acting on `sys.argv`/stdin. So the entire `if __name__ ==
   "__main__":` body here -- the ONLY code in the file that touches a
   graph (`g.load`, the `+{ }` add, the `s{ }` query) -- never executes
   under run_pair, on EITHER side. `customEval` and `inferredSubClass`
   (module level, always defined) are a function and an rdflib Path
   object respectively: neither is an rdflib.Graph nor one of
   rdfeval.harness._comparable's types, so entry=None's module-state
   comparison (`_graphs`/`_values`) finds nothing to compare on either
   side -- not a crash, just "nothing observable to compare", confirmed
   below by actually running it.
2. Even forced to run directly (`python -m ldpy translated.ldpy`, where
   `__name__` genuinely is `"__main__"`), `g.load("foaf.n3")` fails
   immediately and identically on both sides: (a) `Graph.load` does not
   exist on rdflib 7.2.1 (this project's pinned version) -- confirmed via
   `hasattr(Graph(), "load")` -> False, a real API removal, not a typo;
   and (b) even patched to `.parse`, "foaf.n3" is not shipped anywhere in
   this corpus clone (not in the SynBioDex/sbol_factory checkout, not in
   the installed rdflib package's data) -- an external file this example
   script has always depended on and never carried with it.

Neither blocker is a translation artefact: original.py and translated.ldpy
are byte-identical at `g.load("foaf.n3")` (untouched, see meta.json), so
whatever happens there happens on both sides alike.

What IS resolved, and verified by transpiling translated.ldpy in isolation
(`rdfeval check`'s step 1, plus a direct `ldpy.transpiler.transpile` call):
the `s{ SELECT * WHERE { ?s a foaf:Agent . } }` query parses as valid
SPARQL at transpile time -- proving the `PREFIX foaf: <%s> SELECT * WHERE
{ ?s a foaf:Agent . }" % FOAF` interpolation this stratum is about really
does collapse to nothing but a static `@prefix foaf: <...> .` plus a
literal query text, with no runtime string-building left at all. See
meta.json's translation_notes for the full argument and for why
`customEval`/`inferredSubClass`/`CUSTOM_EVALS` (a hand-written SPARQL
algebra BGP rewriter, registered into rdflib's own evaluator) is a
separate, genuine not-expressible finding -- untouched Python either way,
outside anything an island covers.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
