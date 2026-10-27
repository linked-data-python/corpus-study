"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_06-gates_rdodi_procedure_audit_v6_4_0.py__<module>_60.

The region is one module-level line,

    sc = str(rs.value(RES.ResearchCorpus, SKOS.note) or "")

so the oracle is module state (`sc`, plus the graph `rs`).  What it parses is
a sibling file, `{HERE}/01-research/semtech_research_v6_4_0.ttl`, with HERE
the directory of the artefact.  The driver therefore runs the pair once per
INPUT, each in its own scratch directory that holds a copy of the artefacts
and that input as the `01-research` file, and merges the verdicts into one
(a single scenario that differs makes the pair differ).  Each scenario
exercises a path of the line that the others do not:

  shipped      the stand-in shipped with the region: one matching note, a
               neighbouring subject with its own note, another predicate on
               the same subject (a pattern that is too wide would show)
  real         the real landscape/01-research/semtech_research_v6_4_0.ttl of
               the origin repository (corpus/repos/…, commit bad0fa7c46): the
               input the origin script really parses.  `RES` is
               http://example.org/semtech/research#, the file's prefix `sr:`,
               and sr:ResearchCorpus carries ONE note, a language-tagged
               literal ("…"@en)
  zero         no triple res:ResearchCorpus skos:note at all (neighbours
               only): g.value gives None, `or ""` must give "" on both sides
  empty-graph  a Turtle file with no triple
  empty-lit    the note is "": falsy, so `or ""` and str() agree on ""
  zero-lit     the note is 0 (xsd:integer): falsy, "" on both sides, not "0"
  false-lit    the note is false (xsd:boolean): falsy
  zero-str     the note is the plain string "0": truthy, "0" on both sides
  typed        a typed literal ("12"^^xsd:integer): str() of a truthy Literal
  iri          the note is an IRI, not a literal: str() of a URIRef
  multi-*      several notes on the subject, in both orders of the falsy and
               the truthy one: g.value picks one, `.first()` must pick the
               same one (the value of `sc` shows which)
"""
import contextlib
import io
import json
import shutil
import tempfile
from pathlib import Path

from rdfeval.harness import ARTEFACTS, _emit, run_pair

EX_DIR = Path(__file__).resolve().parent
REAL = (EX_DIR.parents[2] / "corpus" / "repos" / "altunelyusuf__SemanticTechnologies"
        / "landscape" / "01-research" / "semtech_research_v6_4_0.ttl")
INPUT = Path("01-research") / "semtech_research_v6_4_0.ttl"

_PRE = """\
@prefix res: <http://example.org/semtech/research#> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .
@prefix dcterms: <http://purl.org/dc/terms/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
res:OtherCollection skos:note "Not the research corpus." .
res:ResearchCorpus dcterms:title "SemTech Research Corpus" .
"""

SCENARIOS = {
    "zero": _PRE,
    "empty-graph": "",
    "empty-lit": _PRE + 'res:ResearchCorpus skos:note "" .\n',
    "zero-lit": _PRE + "res:ResearchCorpus skos:note 0 .\n",
    "false-lit": _PRE + "res:ResearchCorpus skos:note false .\n",
    "zero-str": _PRE + 'res:ResearchCorpus skos:note "0" .\n',
    "typed": _PRE + 'res:ResearchCorpus skos:note "12"^^xsd:integer .\n',
    "iri": _PRE + "res:ResearchCorpus skos:note res:Elsewhere .\n",
    "multi-falsy-first": _PRE + 'res:ResearchCorpus skos:note "", "second" .\n',
    "multi-truthy-first": _PRE + 'res:ResearchCorpus skos:note "first", "" .\n',
    "multi-three": _PRE + 'res:ResearchCorpus skos:note "b", "a", "c" .\n',
}


def _verdict_of(stderr_text: str) -> dict:
    for line in stderr_text.splitlines():
        if line.startswith("RDFEVAL-VERDICT "):
            return json.loads(line[len("RDFEVAL-VERDICT "):])
    raise RuntimeError("run_pair printed no verdict: " + stderr_text[-500:])


def _run(driver_file: Path) -> dict:
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        run_pair(str(driver_file), entry=None, calls=None)
    return _verdict_of(buf.getvalue())


def _scenario_dir(root: Path, name: str, text: str | None, source: Path | None) -> Path:
    d = root / name
    (d / INPUT.parent).mkdir(parents=True)
    for artefact in ARTEFACTS:
        if (EX_DIR / artefact).exists():
            shutil.copy(EX_DIR / artefact, d / artefact)
    if source is not None:
        shutil.copy(source, d / INPUT)
    else:
        (d / INPUT).write_text(text)
    return d


verdicts = {"shipped": _run(EX_DIR / "driver.py")}
with tempfile.TemporaryDirectory() as tmp:
    inputs = {"real": (None, REAL), **{n: (t, None) for n, t in SCENARIOS.items()}}
    for name, (text, source) in inputs.items():
        d = _scenario_dir(Path(tmp), name, text, source)
        verdicts[name] = _run(d / "driver.py")

first = verdicts["shipped"]
VERDICT = {
    "example": EX_DIR.name,
    "equivalent": all(v["equivalent"] for v in verdicts.values()),
    "method": f"module-state x {len(verdicts)} inputs",
    "diffs": [f"[{n}] {d}" for n, v in verdicts.items() for d in v["diffs"]],
    "error": "; ".join(f"[{n}] {v['error']}" for n, v in verdicts.items() if v["error"]) or None,
    "sides": first["sides"],
    "scenarios": sorted(verdicts),
}
_emit(VERDICT)
