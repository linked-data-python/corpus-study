"""Validation driver for synaptixs__ontomesh__tests_test_phase_d_explain.py__test_shacl_rule_attribution.

The region is a test with the `workspace` fixture of its module: a dict of
four paths (ontology, shapes, rules directory, output directory). It runs the
real materializer (materializer.py, verbatim, with the installed owlrl and
pyshacl), asks `explain_triple` for the lineage of (:t1, :flag, "true") and,
when that comes back empty, reads the lineage graph itself and asserts what
the derivation of that triple looks like. It returns None, so what the
original SHOWS is whether it raises.

The driver builds the `workspace` dict from the files of `work/` (static,
inside the example directory, so the paths are the same for both sides; the
output directory of a case is `work/out_<case>`, whose files the harness
compares between the sides and removes). The cases differ in the SHACL shapes
only; the ontology (:t1 a :Trigger, a two-hop :partOf chain for the SPARQL
rule) and the SPARQL rule are shared. The clock and the stopwatch of the
materializer are frozen before each call (same for both representations):
the activity IRIs, the timestamps and the durations they write would
otherwise differ between the two runs.

  fallback        the test's own shapes: SHACL derives :t1 :flag true
                  (xsd:boolean), explain_triple's lookup for the plain
                  literal "true" misses, the region reads the lineage itself:
                  one reified statement, rule id "shacl:TriggerShape",
                  engine "shacl" -> passes.
  direct          the shape's object is the string "true": explain_triple
                  finds the derivation, the fallback does not run -> passes
                  with no read of the region executed.
  no_rule_fired   the shape targets a class :t1 is not in: no statement about
                  (:t1, :flag) -> "no lineage record".
  renamed         the right statement, derived by :FlagShape: the rule id does
                  not contain "Trigger" -> AssertionError.
  wrong_subject   a statement (:t2, :flag) whose rule is :TriggerShape and
                  none for :t1 -> "no lineage record" (a check on the
                  predicate alone would pick it and pass).
  wrong_predicate a statement (:t1, :mark) whose rule is :TriggerMarkShape
                  and none for :flag -> "no lineage record" (a check on the
                  subject alone would pick it and pass).
  both            :MarkShape (rule id without "Trigger") derives (:t1, :mark)
                  and :TriggerShape derives (:t1, :flag): the region must
                  skip the first statement whatever order the file lists
                  them in, and pass.
"""
import types
from datetime import datetime as _datetime
from pathlib import Path

from rdfeval.harness import run_pair
import materializer

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"


class _Frozen(_datetime):
    @classmethod
    def now(cls, tz=None):
        return _datetime(2026, 1, 1, 12, 0, 0, tzinfo=tz)


def _case(shapes, name):
    def make():
        materializer.datetime = _Frozen
        materializer.time = types.SimpleNamespace(perf_counter=lambda: 0.0)
        workspace = {
            "ontology": str(WORK / "enterprise.ttl"),
            "shapes": str(WORK / shapes),
            "rules_dir": str(WORK / "rules"),
            "out": str(WORK / f"out_{name}"),
        }
        return (workspace,), {}
    return make


CALLS = [
    _case("shapes_trigger.ttl", "fallback"),
    _case("shapes_string.ttl", "direct"),
    _case("shapes_other_class.ttl", "no_rule_fired"),
    _case("shapes_renamed.ttl", "renamed"),
    _case("shapes_wrong_subject.ttl", "wrong_subject"),
    _case("shapes_wrong_predicate.ttl", "wrong_predicate"),
    _case("shapes_both.ttl", "both"),
]

VERDICT = run_pair(
    __file__,
    entry='test_shacl_rule_attribution',
    calls=CALLS,
)
