"""Validation driver for danilipp17__thesis_code__oscin_reader.py__OntologyReader__read_agents.

This region only READS a graph: for one agent it follows
``employsReasoningPattern`` to a reasoning-pattern individual and recovers the
pattern's name from its ``rdf:type``.  Its result is ``reasoning_pattern``,
which the enclosing method (oscin/reader.py:249-262) stores on the agent.

1. ``run_pair(entry=None)`` runs both modules top to bottom, on the small
   graph they build inline, and compares every module value and stdout.

2. That graph holds one agent with one pattern, so it cannot tell the anchor
   ``{agent_uri}`` from a variable, nor show that the outer loop moves on to
   the next pattern when the first one has no recognised type.  The driver
   therefore runs each module again on the graphs of CASES below.  Each run
   executes the artefact's own text with ONE line changed: the context line
   ``self = _Self(g)`` becomes ``self = _Self(<case graph>)``, so the region
   reads the case graph instead of the inline one.  The agent stays
   ``agent_uri`` = <http://example.org/agent/1>, a URIRef, as the repository
   passes it (it comes from ``self.g.subjects(RDF.type, AGENTO.LLMAgent)``).
   Compared per case: ``reasoning_pattern`` and stdout.

   Two cases go beyond what the repository's populator writes ("exactly
   one such triple", reader.py:249): an agent with TWO recognised patterns,
   in both insertion orders.  They make the ``break`` observable (the first
   recognised pair wins, not the last).  Which pair is first is store
   order: the nested ``objects()`` loops and the BGP of ``m{ }`` both walk
   the fresh Memory store in insertion order, pattern by pattern, so the two
   sides agree here; a store that ordered them differently would make these
   two cases fail, and that failure would be the equivalence's real
   dependency on order, not noise.
"""
import contextlib
import io
import sys
import traceback
from pathlib import Path

from rdflib import Graph

from rdfeval import harness
from rdfeval.harness import _emit, run_pair

EX_DIR = Path(__file__).resolve().parent
ANCHOR = "self = _Self(g)"
SUBSTITUTE = "self = _Self(__case_graph__)"

PREFIXES = """
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix ao: <http://www.semanticweb.org/danilippmann/ontologies/2026/3/agentoscin/> .
@prefix agent: <http://example.org/agent/> .
@prefix rp: <http://example.org/rp/> .
"""

CASES = {
    # The outer loop must move past a pattern with no recognised type to the
    # next one.  agent/2's pattern must not be read: it is another agent's.
    # agent/1 also reaches a TreeOfThoughts individual through rdfs:seeAlso,
    # a neighbour predicate that must not be followed.
    "unrecognised-then-recognised": """
        agent:1 ao:employsReasoningPattern rp:a , rp:b ;
                rdfs:seeAlso rp:seen .
        rp:a a owl:NamedIndividual , ao:SomeOtherPattern .
        rp:b a owl:NamedIndividual , ao:ChainOfThought .
        agent:2 ao:employsReasoningPattern rp:c .
        rp:c a owl:NamedIndividual , ao:ReAct .
        rp:seen a ao:TreeOfThoughts .
    """,
    # agent/1's only pattern has no recognised type, while the neighbour
    # agent/2 has one: the answer is "" (kills {agent_uri} -> a variable).
    "neighbour-agent-only": """
        agent:1 ao:employsReasoningPattern rp:a .
        rp:a a owl:NamedIndividual .
        agent:2 ao:employsReasoningPattern rp:c .
        rp:c a owl:NamedIndividual , ao:ReflectionLoop .
    """,
    # No employsReasoningPattern at all for agent/1: a recognised pattern is
    # reachable only through another predicate (kills the predicate widened
    # to a variable).  Zero solutions: "".
    "no-pattern": """
        agent:1 rdfs:seeAlso rp:seen ;
                ao:hasReasoningEnabled true .
        rp:seen a ao:ReAct .
    """,
    # The pattern names its class through a predicate other than rdf:type
    # (kills rdf:type widened to a variable): "".
    "class-not-by-rdf-type": """
        agent:1 ao:employsReasoningPattern rp:a .
        rp:a rdfs:seeAlso ao:TreeOfThoughts ;
             a owl:NamedIndividual .
    """,
    # The repository's own shape: one pattern, its class plus
    # owl:NamedIndividual.
    "single-pattern": """
        agent:1 ao:employsReasoningPattern rp:t .
        rp:t a ao:TreeOfThoughts , owl:NamedIndividual .
    """,
    # A recognised class without owl:NamedIndividual (kills an extra
    # conjunct on owl:NamedIndividual in the join).
    "class-only": """
        agent:1 ao:employsReasoningPattern rp:t .
        rp:t a ao:ReAct .
    """,
    # Two recognised patterns: the first one met wins (the ``break``).
    "two-recognised": """
        agent:1 ao:employsReasoningPattern rp:x .
        rp:x a ao:ReAct .
        agent:1 ao:employsReasoningPattern rp:y .
        rp:y a ao:ChainOfThought .
    """,
    "two-recognised-reversed": """
        agent:1 ao:employsReasoningPattern rp:y .
        rp:y a ao:ChainOfThought .
        agent:1 ao:employsReasoningPattern rp:x .
        rp:x a ao:ReAct .
    """,
    # An empty graph.
    "empty": "",
}


def _case_graph(turtle: str) -> Graph:
    """A fresh graph per side and per case."""
    return Graph().parse(data=PREFIXES + turtle, format="turtle")


def _run_on(filename: str, graph: Graph) -> tuple[object, str]:
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
    return ns["reasoning_pattern"], out.getvalue()


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
            if ro != rt:
                diffs.append(f"case {name}: reasoning_pattern differs ({ro!r} vs {rt!r})")
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
