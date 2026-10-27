"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_06-gates_semtech_supplementary_gates_v1_0_0.py__<module>_149.

Module-level script (kind="statement"), so entry=None: the artefacts are
executed as modules and every module-level value is compared -- the parsed
`g_ab` graph (isomorphism) and, crucially, the derived `ex_no_prov` list of
strings, IN ORDER (module-state values are compared in order: the list
comprehension of the original follows the graph's iteration order).

The artefacts parse `{H}/02-ontology/semtech_abox_v1_0_0.ttl`, `H` being a
constant imported from the context shim (context.py).  On the REAL file of
the origin repository `ex_no_prov == []` (the 120 T-prefixed individuals all
carry a provenance), so that input alone is a hollow green: no positive case
is ever produced.  The driver therefore runs the pair on several inputs, by
pointing `context.H` (the shim's attribute, which the artefacts read when
they import it) at a scratch directory holding a synthetic abox, and merges
the verdicts into one: a single scenario that differs makes the pair differ.

  real         the real abox of the origin repository (as before): the input
               the origin script really parses, result empty
  mixed        every branch of the region, in ONE graph (SEM = semtech#):
                 z1  NamedIndividual, TWO T-types, no provenance  -> listed once
                 a2  one T-type, no provenance                    -> listed
                 x3/y4/x3  interleaved: x3 T1, y4 T1, x3 T2       -> graph order x3, y4
                 m5  provenance "" (falsy literal)                -> listed
                 n6  provenance 0 (falsy literal)                 -> listed
                 f7  provenance false (falsy literal)             -> listed
                 s8  provenance "0" (truthy string)               -> not listed
                 p9  provenance "ok"                              -> not listed
                 u10 provenance an IRI                            -> not listed
                 v11 provenance "" then "ok" (two values, falsy first)
                 w12 provenance "ok" then "" (two values, truthy first)
                 q13 only a non-T type (semtech#Other)            -> not listed
                 r14 T-typed but NOT an owl:NamedIndividual       -> not listed
                 t15 NamedIndividual with no other type           -> not listed
                 o16 T-type of another namespace (other#Tx)       -> not listed
                 l17 lower-case t-type (semtech#tx)               -> not listed
  reversed     the same subjects in the opposite order of appearance, so an
               ordering that came from a set or a sort rather than from the
               graph is seen
  none-named   T-typed resources, none an owl:NamedIndividual: zero solution
  empty        a file with no triple at all
"""
import contextlib
import io
import json
import tempfile
from pathlib import Path

import context
from rdfeval.harness import _emit, run_pair

_PRE = """\
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix sem: <http://example.org/semtech#> .
@prefix other: <http://example.org/other#> .
@prefix ex: <http://example.org/ind#> .
"""

# one block per individual, so the "reversed" scenario can flip their order
_BLOCKS = [
    "ex:z1 a owl:NamedIndividual, sem:TypeA, sem:TypeB .\n",
    "ex:a2 a owl:NamedIndividual, sem:TypeA .\n",
    # x3 and y4 interleaved on purpose: the join yields rows x3, y4, x3
    "ex:x3 a owl:NamedIndividual, sem:TypeA .\n"
    "ex:y4 a owl:NamedIndividual, sem:TypeA .\n"
    "ex:x3 a sem:TypeB .\n",
    'ex:m5 a owl:NamedIndividual, sem:TypeA ; sem:hasSourceProvenance "" .\n',
    "ex:n6 a owl:NamedIndividual, sem:TypeA ; sem:hasSourceProvenance 0 .\n",
    "ex:f7 a owl:NamedIndividual, sem:TypeA ; sem:hasSourceProvenance false .\n",
    'ex:s8 a owl:NamedIndividual, sem:TypeA ; sem:hasSourceProvenance "0" .\n',
    'ex:p9 a owl:NamedIndividual, sem:TypeA ; sem:hasSourceProvenance "ok" .\n',
    "ex:u10 a owl:NamedIndividual, sem:TypeA ; sem:hasSourceProvenance ex:src .\n",
    'ex:v11 a owl:NamedIndividual, sem:TypeA ; sem:hasSourceProvenance "", "ok" .\n',
    'ex:w12 a owl:NamedIndividual, sem:TypeA ; sem:hasSourceProvenance "ok", "" .\n',
    "ex:q13 a owl:NamedIndividual, sem:Other .\n",
    "ex:r14 a sem:TypeA .\n",
    "ex:t15 a owl:NamedIndividual .\n",
    "ex:o16 a owl:NamedIndividual, other:Tx .\n",
    "ex:l17 a owl:NamedIndividual, sem:tx .\n",
]

SCENARIOS = {
    "mixed": _PRE + "".join(_BLOCKS),
    "reversed": _PRE + "".join(reversed(_BLOCKS)),
    "none-named": _PRE + "ex:r1 a sem:TypeA .\nex:r2 a sem:TypeB, sem:TypeC .\n",
    "empty": "",
}


def _verdict_of(stderr_text: str) -> dict:
    for line in stderr_text.splitlines():
        if line.startswith("RDFEVAL-VERDICT "):
            return json.loads(line[len("RDFEVAL-VERDICT "):])
    raise RuntimeError("run_pair printed no verdict: " + stderr_text[-500:])


def _run() -> dict:
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        run_pair(__file__, entry=None, calls=None)
    return _verdict_of(buf.getvalue())


real_h = context.H
verdicts = {"real": _run()}
with tempfile.TemporaryDirectory() as tmp:
    for name, text in SCENARIOS.items():
        d = Path(tmp) / name / "02-ontology"
        d.mkdir(parents=True)
        (d / "semtech_abox_v1_0_0.ttl").write_text(text)
        context.H = str(Path(tmp) / name)
        verdicts[name] = _run()
context.H = real_h

VERDICT = {
    "example": Path(__file__).resolve().parent.name,
    "equivalent": all(v["equivalent"] for v in verdicts.values()),
    "method": f"module-state x {len(verdicts)} inputs",
    "diffs": [f"[{n}] {d}" for n, v in verdicts.items() for d in v["diffs"]],
    "error": "; ".join(f"[{n}] {v['error']}" for n, v in verdicts.items() if v["error"]) or None,
    "sides": verdicts["real"]["sides"],
    "scenarios": sorted(verdicts),
}
_emit(VERDICT)
