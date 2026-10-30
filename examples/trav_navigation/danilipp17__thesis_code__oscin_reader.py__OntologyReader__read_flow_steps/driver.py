"""Validation driver for danilipp17__thesis_code__oscin_reader.py__OntologyReader__read_flow_steps.

The region READS a graph and fills two module-level dicts, ``step_info`` and
``step_uri_to_name``, for the workflow pattern ``wp_uri``.

1. ``run_pair(entry=None)`` runs both modules top to bottom on fixture.ttl
   (one step of each step_type, every optional field, a foreign workflow)
   and compares every module value and stdout.

2. fixture.ttl has one keyed associated agent per step, so it cannot show
   the ``break`` of the agent search, nor several combinations of types.
   The driver therefore runs each module again on the graphs of CASES
   (repair 2026-10-30).  Each run executes the artefact's own text with ONE
   line changed: the context line ``self, wp_uri = build_fixture()`` becomes
   ``self, wp_uri = __case__``, where ``__case__`` is a fresh shim
   ``_Reader`` over the case graph (same agent-key map on both sides) and
   ``wp_uri`` = wp:W, a URIRef, as the repository passes it (it comes from
   ``self.g.objects(orch_uri, AGENTO.hasWorkflowPattern)``, reader.py:671,
   and the populator mints URIRefs, populator.py:801).  Compared per case:
   ``step_info``, ``step_uri_to_name`` and stdout.

   Two keyed agents on one step, in both insertion orders, make the
   ``break`` observable: the first keyed agent met wins.  Which is first is
   store order: ``g.objects()`` and ``m{ }`` both walk the fresh Memory
   store in insertion order, so the two sides agree; a store that ordered
   them differently would fail these two cases, and that would be a real
   dependency of the equivalence on order, not noise.  The repository's
   populator links at most one agent per step (populator.py:913-920), so
   these two cases go beyond what it writes.
"""
import contextlib
import io
import sys
import traceback
from pathlib import Path

from rdflib import Graph, URIRef

from rdfeval import harness
from rdfeval.harness import _emit, run_pair

EX_DIR = Path(__file__).resolve().parent
ANCHOR = "self, wp_uri = build_fixture()"
SUBSTITUTE = "self, wp_uri = __case__"
WP = URIRef("http://example.org/workflows#W")
KEYS = {
    "http://example.org/agents#a": "agent_a",
    "http://example.org/agents#b": "agent_b",
    "http://example.org/agents#empty": "",
}

PREFIXES = """
@prefix agento: <http://www.w3id.org/agentic-ai/onto#> .
@prefix ao: <http://www.semanticweb.org/danilippmann/ontologies/2026/3/agentoscin/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix wp: <http://example.org/workflows#> .
@prefix step: <http://example.org/steps#> .
@prefix ag: <http://example.org/agents#> .
"""

CASES = {
    # Two keyed agents: the first one met wins (the ``break``).
    "two-keyed-agents": """
        wp:W agento:hasWorkflowStep step:S .
        step:S ao:hasAssociatedAgent ag:a .
        step:S ao:hasAssociatedAgent ag:b .
    """,
    "two-keyed-agents-reversed": """
        wp:W agento:hasWorkflowStep step:S .
        step:S ao:hasAssociatedAgent ag:b .
        step:S ao:hasAssociatedAgent ag:a .
    """,
    # Unknown agent and an agent whose key is "" (falsy) before a keyed one:
    # the search moves past both.  A keyed agent reached through another
    # predicate must not be read.
    "falsy-keys-then-keyed": """
        wp:W agento:hasWorkflowStep step:S .
        step:S ao:hasAssociatedAgent ag:unknown , ag:empty , ag:b ;
               rdfs:seeAlso ag:a .
    """,
    # Only unkeyed agents, and a keyed one on ANOTHER step outside W:
    # associated_agent_key stays None (kills {step_uri} widened).
    "no-keyed-agent": """
        wp:W agento:hasWorkflowStep step:S .
        step:S ao:hasAssociatedAgent ag:unknown .
        step:T ao:hasAssociatedAgent ag:a .
    """,
    # Start AND conditional -> "start", routing logic still read.
    # End AND conditional -> "conditional".  Start AND end -> "start".
    "type-combinations": """
        wp:W agento:hasWorkflowStep step:SC , step:EC , step:SE .
        step:SC a agento:StartStep , ao:ConditionalStep ;
                ao:hasRoutingLogic "x > 1" .
        step:EC a agento:EndStep , ao:ConditionalStep ;
                ao:hasRoutingLogic "y" .
        step:SE a agento:StartStep , agento:EndStep .
    """,
    # Step types, next steps, decorator arguments and agents reached through
    # neighbour predicates only: every field at its default (kills each
    # predicate widened to a variable).
    "neighbour-predicates": """
        wp:W agento:hasWorkflowStep step:S .
        step:S rdfs:seeAlso agento:StartStep , ao:ConditionalStep ,
                            agento:EndStep , step:N , "arg" , ag:a ;
               rdfs:comment "not a decorator argument" .
    """,
    # Several next steps and decorator arguments, an IRI among the
    # arguments (skipped by isinstance), a language-tagged one.
    "many-values": """
        wp:W agento:hasWorkflowStep step:S .
        step:S agento:nextStep step:A , step:B , step:C ;
               ao:hasDecoratorArgument "one" , "deux"@fr , step:NotALiteral .
    """,
    # W has no step; another workflow has one: both dicts stay empty.
    "no-steps": """
        wp:Other agento:hasWorkflowStep step:S .
        step:S a agento:StartStep ; agento:hasTitle "foreign" .
        wp:W rdfs:seeAlso step:T .
    """,
    # An empty graph.
    "empty": "",
}


def _case_graph(turtle: str) -> Graph:
    """A fresh graph per side and per case."""
    return Graph().parse(data=PREFIXES + turtle, format="turtle")


def _run_on(filename: str, graph: Graph):
    """Execute one artefact with the case reader in place of the fixture."""
    import shim
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
          "__case__": (shim._Reader(graph, dict(KEYS)), WP)}
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        exec(compile(source, str(path), "exec"), ns)
    return (ns["step_info"], ns["step_uri_to_name"]), out.getvalue()


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
            results[name] = len(ro[0])
            if ro != rt:
                diffs.append(f"case {name}: step_info/step_uri_to_name differ "
                             f"({ro!r} vs {rt!r})")
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
