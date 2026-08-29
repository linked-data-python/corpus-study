"""Validation driver for d3fend__d3fend-ontology__src_util_update_attack.py__update_definition.

Establishes semantic equivalence of original.py and translated.ldpy by
calling update_definition(graph, tech, framework) once, on a graph that
already carries the attack_id as a bare literal (so the coercion_datatype
site -- `(None, None, Literal(attack_id)) in graph` -- takes its True branch)
but has no d3fend:definition yet for the attack (so the function adds one and
returns 1). Both the return value and the mutated `graph` are compared.

The fixture is a callable, not a literal (args, kwargs) tuple: `graph` is
mutated in place by the function under test, so each side needs its own
fresh Graph instance (see rdfeval.harness.run_pair).
"""
from rdfeval.harness import run_pair


def _fixture():
    from rdflib import Graph, URIRef, RDFS, Literal
    graph = Graph()
    # Neighbouring triple, unrelated predicate: exercises the wildcard ?s ?p
    # of the coercion_datatype site without being the definition triple
    # itself.
    graph.add((URIRef("http://example.org/technique/T1055"), RDFS.label, Literal("T1055")))
    tech = {
        "data": {
            "external_references": [
                {"source_name": "mitre-attack", "external_id": "T1055"},
            ],
            "description": "Process Injection.\nAdversaries may inject code into running processes.",
        }
    }
    framework = "enterprise"
    return ((graph, tech, framework), {})


VERDICT = run_pair(
    __file__,
    entry='update_definition',
    calls=[_fixture],
)
