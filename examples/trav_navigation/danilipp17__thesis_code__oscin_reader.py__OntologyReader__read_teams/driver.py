"""Validation driver for danilipp17__thesis_code__oscin_reader.py__OntologyReader__read_teams.

The region READS a graph: for one team it walks ``hasTerminationCondition``,
dispatches on each condition's type, descends into a Composite's
``hasSubCondition``, and leaves two results, ``max_turns`` and
``termination_conditions``, which the enclosing method
(oscin/reader.py:528-605) stores on the team.

1. ``run_pair(entry=None)`` runs both modules top to bottom, on the graph
   they build inline (one team, the four branches, a Composite with two
   sub-conditions), and compares every module value and stdout.

2. That graph holds one team and one Composite, every TurnLimit has a
   maxTurns, every EventBased a trigger, the Composite an operator.  So it
   cannot tell the anchors ``{team_uri}`` and ``{term_uri}`` from variables,
   nor observe the guards ``mt is not None`` and the defaults ``or "OR"`` and
   ``or ""``.  The driver therefore runs each module again on the graphs of
   CASES below.  Each run executes the artefact's own text with ONE line
   changed: the context line ``self = ReaderSelf(g)`` becomes
   ``self = ReaderSelf(<case graph>)``, so the region (and the shim's
   ``_int_value``/``_str_value``, which read ``self.g``) reads the case graph.
   The team stays ``team_uri`` = ``AGENTOSCIN.team1``, a URIRef, as the
   repository passes it (it comes from ``self.g.subjects(RDF.type, …)``).
   Compared per case: ``max_turns``, ``termination_conditions`` (as a list:
   both sides walk the fresh Memory store in insertion order) and stdout.
"""
import contextlib
import io
import sys
import traceback
from pathlib import Path

from rdflib import Graph

from rdfeval import harness
from rdfeval.harness import _compare_value, _emit, run_pair

EX_DIR = Path(__file__).resolve().parent
ANCHOR = "self = ReaderSelf(g)"
SUBSTITUTE = "self = ReaderSelf(__case_graph__)"

PREFIXES = """
@prefix ao: <http://www.semanticweb.org/danilippmann/ontologies/2026/3/agentoscin/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

CASES = {
    # team1 next to a fully furnished team2 that must not be read.
    #  - ao:tl_none: a TurnLimit without maxTurns (``mt is not None`` false),
    #    ao:tl_bad: a maxTurns that is not an integer (_int_value -> None);
    #  - ao:ev_none: an EventBased without trigger (the ``or ""`` default);
    #  - ao:comp1: a Composite without operator (the ``or "OR"`` default),
    #    whose sub-conditions are an EventBased "sub1", an EventBased
    #    without trigger, a TurnLimit without maxTurns, a TurnLimit 4 (not
    #    promoted: ao:tl_5 already set max_turns), and a condition of
    #    unknown type; a further EventBased hangs off comp1 through a
    #    neighbour predicate (ao:hasOtherCondition) and must be ignored;
    #  - ao:unknown: a condition whose type is in no branch.  It and
    #    ao:sub_unknown carry a maxTurns and a trigger, and name every class
    #    of the elif chain through ao:relatedClass instead of rdf:type, so a
    #    type test widened in its subject or its predicate would take them;
    #  - ao:side: a TurnLimit 42 reached through a neighbour predicate.
    # team2's conditions and its Composite's sub-conditions would show up in
    # team1's answer if ``{team_uri}`` or ``{term_uri}`` were widened.
    "two-teams": """
        ao:team1 ao:hasTerminationCondition ao:tl_5 , ao:tl_none , ao:tl_bad ,
                     ao:ev_none , ao:comp1 , ao:unknown ;
                 ao:hasOtherCondition ao:side .
        ao:tl_5 a ao:TurnLimitTermination ; ao:hasMaxTurns 5 .
        ao:tl_none a ao:TurnLimitTermination .
        ao:tl_bad a ao:TurnLimitTermination ; ao:hasMaxTurns "many" .
        ao:ev_none a ao:EventBasedTermination .
        ao:comp1 a ao:CompositeTermination ;
                 ao:hasSubCondition ao:sub_ev1 , ao:sub_ev_none , ao:sub_tl_none , ao:sub_tl4 ,
                                    ao:sub_unknown ;
                 ao:hasOtherCondition ao:not_a_sub .
        ao:sub_ev1 a ao:EventBasedTermination ; ao:hasTriggerExpression "sub1" .
        ao:sub_ev_none a ao:EventBasedTermination .
        ao:sub_tl_none a ao:TurnLimitTermination .
        ao:sub_tl4 a ao:TurnLimitTermination ; ao:hasMaxTurns 4 .
        ao:sub_unknown a ao:SomeOtherTermination ;
                       ao:relatedClass ao:TurnLimitTermination , ao:EventBasedTermination ;
                       ao:hasMaxTurns 11 ; ao:hasTriggerExpression "sub-unknown" .
        ao:not_a_sub a ao:EventBasedTermination ; ao:hasTriggerExpression "not-a-sub" .
        ao:unknown a ao:SomeOtherTermination ;
                   ao:relatedClass ao:TurnLimitTermination , ao:EventBasedTermination ,
                                   ao:RoutingTermination , ao:CompositeTermination ;
                   ao:hasMaxTurns 12 ; ao:hasTriggerExpression "unknown" .
        ao:side a ao:TurnLimitTermination ; ao:hasMaxTurns 42 .

        ao:team2 ao:hasTerminationCondition ao:t2_tl , ao:t2_ev , ao:t2_rt , ao:t2_comp .
        ao:t2_tl a ao:TurnLimitTermination ; ao:hasMaxTurns 99 .
        ao:t2_ev a ao:EventBasedTermination ; ao:hasTriggerExpression "team2" .
        ao:t2_rt a ao:RoutingTermination .
        ao:t2_comp a ao:CompositeTermination ; ao:hasOperator "AND" ;
                   ao:hasSubCondition ao:t2_sub_ev , ao:t2_sub_tl .
        ao:t2_sub_ev a ao:EventBasedTermination ; ao:hasTriggerExpression "team2-sub" .
        ao:t2_sub_tl a ao:TurnLimitTermination ; ao:hasMaxTurns 77 .
    """,
    # No top-level TurnLimit: the first TurnLimit sub-condition is promoted
    # to max_turns, the second is not (``if max_turns is None``).
    "promotion": """
        ao:team1 ao:hasTerminationCondition ao:comp .
        ao:comp a ao:CompositeTermination ; ao:hasOperator "OR" ;
                ao:hasSubCondition ao:sub_a , ao:sub_b .
        ao:sub_a a ao:TurnLimitTermination ; ao:hasMaxTurns 3 .
        ao:sub_b a ao:TurnLimitTermination ; ao:hasMaxTurns 8 .
        ao:team2 ao:hasTerminationCondition ao:t2_tl .
        ao:t2_tl a ao:TurnLimitTermination ; ao:hasMaxTurns 99 .
    """,
    # A Composite with no sub-condition at all, and a Routing condition.
    "empty-composite": """
        ao:team1 ao:hasTerminationCondition ao:comp , ao:rt .
        ao:comp a ao:CompositeTermination ; ao:hasOperator "AND" .
        ao:rt a ao:RoutingTermination .
    """,
    # team1 has no condition (zero solutions), team2 has some.
    "no-condition": """
        ao:team2 ao:hasTerminationCondition ao:t2_tl .
        ao:t2_tl a ao:TurnLimitTermination ; ao:hasMaxTurns 99 .
    """,
    # An empty graph.
    "empty": "",
}

RESULTS = ("max_turns", "termination_conditions")


def _case_graph(turtle: str) -> Graph:
    """A fresh graph per side and per case."""
    return Graph().parse(data=PREFIXES + turtle, format="turtle")


def _run_on(filename: str, graph: Graph) -> tuple[dict, str]:
    """Execute one artefact with the case graph in place of the inline one."""
    path = harness._redirected(EX_DIR / filename)
    harness._EXECUTED.append(path.name)
    source = path.read_text()
    if source.count(ANCHOR) != 1:
        raise RuntimeError(f"{path.name}: context line {ANCHOR!r} not found once")
    source = source.replace(ANCHOR, SUBSTITUTE)
    if path.suffix == ".ldpy":
        from ldpy.transpiler import transpile
        source = transpile(source, filename=str(path)).code
    ns = {"__name__": f"__case_{path.stem}__", "__file__": str(path),
          "__case_graph__": graph}
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(source, str(path), "exec"), ns)
    return {k: ns[k] for k in RESULTS}, out.getvalue()


# 1. The modules as they are (run_pair's own verdict, emitted below once).
with contextlib.redirect_stderr(io.StringIO()):
    verdict = run_pair(__file__, entry=None, calls=None)

# 2. The same modules on each case graph.
diffs = list(verdict.get("diffs") or [])
results = {}
if not verdict.get("error"):
    try:
        for name, turtle in CASES.items():
            ro, out_o = _run_on("original.py", _case_graph(turtle))
            rt, out_t = _run_on("translated.ldpy", _case_graph(turtle))
            results[name] = ro
            for key in RESULTS:
                _compare_value(ro[key], rt[key], f"case {name}: {key}", diffs)
            if out_o != out_t:
                diffs.append(f"case {name}: stdout differs ({out_o!r} vs {out_t!r})")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)

verdict["method"] = "module-state + cases"
verdict["cases"] = results
verdict["diffs"] = diffs
verdict["equivalent"] = not diffs and not verdict.get("error")
VERDICT = verdict
_emit(verdict)
sys.exit(0)
