"""Validation driver for laBioSynCare__laBioSynCare.github.io__scripts_sstim-ecosystem-contract.py__check_positive_contract.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a block of statements (the activity loop of the repository's
check_positive_contract), restored at module level: both modules are
executed and every rdflib Graph and every comparable module-level value is
compared (run_pair's module-state mode) -- above all `errors`, the list of
messages the loop appends.

The project's own fixture (scenario 0) is purely positive: `errors` stays
empty, so it cannot tell a traversal from its removal.  Both modules
therefore read their fixture and their context file through a seam that is
identical on both sides (RDFEVAL_SSTIM_FIXTURE / RDFEVAL_SSTIM_CONTEXT, see
the context lines of original.py), and the module pair is run once per
scenario:

* 0 -- fixture.ttl, the project's real positive fixture, no context file
  (the original single run, unchanged);
* 1 -- fixture_edge.ttl + context_edge.ttl: one failing requirement per
  activity -- zero, two and mismatched inbound relationships; a consent
  decision governed by PERSON, one by someone else, one with no
  relationship; an activity that only points at the consent class through
  rdfs:seeAlso; PERSON not a prov:Agent (a prov:Person, and rdfs:seeAlso
  prov:Agent); CURATOR a prov:Agent ONLY in `merged` (the context file), so
  a test made against `fixture` instead of `merged` differs; predecessors
  earlier, later, without and with two timestamps, a literal one, a
  blank-node one, one reached through prov:wasInfluencedBy (must not be
  visited) and one pointing the other way; events with no, two and an
  xsd:date timestamp;
* 2 -- fixture_edge.ttl alone: CURATOR is then not a prov:Agent anywhere;
* 3 -- fixture_empty.ttl: no activity at all (zero solutions).

The four verdicts are folded into one: equivalent only if every scenario
is, and each scenario's differences are reported under its name.
"""
import contextlib
import io
import os
from pathlib import Path

from rdfeval.harness import _emit, run_pair

HERE = Path(__file__).resolve().parent

SCENARIOS = [
    ("real-fixture", None, None),
    ("edge+context", "fixture_edge.ttl", "context_edge.ttl"),
    ("edge-no-context", "fixture_edge.ttl", None),
    ("empty", "fixture_empty.ttl", None),
]


def _run(fixture, context):
    saved = {k: os.environ.get(k)
             for k in ("RDFEVAL_SSTIM_FIXTURE", "RDFEVAL_SSTIM_CONTEXT")}
    for key, name in (("RDFEVAL_SSTIM_FIXTURE", fixture),
                      ("RDFEVAL_SSTIM_CONTEXT", context)):
        if name:
            os.environ[key] = str(HERE / name)
        else:
            os.environ.pop(key, None)
    try:
        with contextlib.redirect_stderr(io.StringIO()):  # one verdict line only
            return run_pair(__file__, entry=None, calls=None)
    finally:
        for key, value in saved.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


verdicts = [(label, _run(fx, ctx)) for label, fx, ctx in SCENARIOS]
VERDICT = dict(verdicts[0][1])
VERDICT["method"] = "module-state x%d scenarios" % len(verdicts)
VERDICT["diffs"] = [f"{label}: {d}" for label, v in verdicts for d in v["diffs"]]
errors = [f"{label}: {v['error']}" for label, v in verdicts if v.get("error")]
VERDICT["error"] = "\n".join(errors) or None
VERDICT["scenarios"] = {label: {"equivalent": v["equivalent"],
                                "values_compared": v.get("values_compared")}
                        for label, v in verdicts}
VERDICT["equivalent"] = all(v["equivalent"] for _, v in verdicts)
_emit(VERDICT)
