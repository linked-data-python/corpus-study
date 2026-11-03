# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/reader.py
# region: OntologyReader._read_flow_steps (lines 711-789, stratum trav_navigation)
# licence of the source repository: see meta.json
import json
from typing import Optional
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD
from shim import (  # context shim (see meta.json)
    AGENTO,
    AGENTOSCIN,
    CALLS_CREW,
    COORD_CUSTOM,
    COORD_SEQUENTIAL,
    HAS_DESCRIPTION,
    HAS_TITLE,
)

# Test harness only (see meta.json): binds self/wp_uri from the fixture and
# the two accumulators the region writes into, so the extracted statements
# run standalone. Added identically to original.py and translated.ldpy.
from shim import build_fixture

self, wp_uri = build_fixture()
step_uri_to_name: dict[str, str] = {}
step_info: dict[str, dict] = {}

for step_uri in self.g.objects(wp_uri, AGENTO.hasWorkflowStep):
    name = self._str_value(step_uri, HAS_TITLE) or self._local_name(step_uri)

    # Determine step type from RDF type
    is_start = (step_uri, RDF.type, AGENTO.StartStep) in self.g
    is_conditional = (step_uri, RDF.type, AGENTOSCIN.ConditionalStep) in self.g

    # A step can be both start and conditional (LangGraph pattern:
    # entry node with conditional edges). EndStep is mutually
    # exclusive with StartStep — a start step is never just "end".
    if is_conditional and not is_start:
        step_type = "conditional"
    elif is_start:
        step_type = "start"
    elif (step_uri, RDF.type, AGENTO.EndStep) in self.g:
        step_type = "end"
    else:
        step_type = "regular"

    # Read edge mapping (label → target node mapping)
    try:
        edge_mapping = json.loads(self._str_value(step_uri, AGENTOSCIN.hasEdgeMapping) or "{}")
    except (json.JSONDecodeError, TypeError):
        edge_mapping = {}

    step_info[str(step_uri)] = {
        "order": self._int_value(step_uri, AGENTO.stepOrder) or 0,
        "name": name,
        "step_type": step_type,
        # Read routing logic for any conditional step (including start+conditional)
        "routing_logic": (self._str_value(step_uri, AGENTOSCIN.hasRoutingLogic) or ""
                          if is_conditional else ""),
        "edge_mapping": edge_mapping,
        # Collect nextStep targets
        "next_uris": [str(next_uri) for next_uri in self.g.objects(step_uri, AGENTO.nextStep)],
        # Original literal decorator arguments (e.g. CrewAI
        # @start("wait_next_run")) preserved by the populator. These
        # are restored ahead of the inferred dependency list.
        "decorator_args": [
            str(lit) for lit in self.g.objects(step_uri, AGENTOSCIN.hasDecoratorArgument)
            if isinstance(lit, Literal)],
        # Associated agent (e.g. LangGraph node → LLMAgent)
        "associated_agent_key": next(filter(None, (
            self._agent_uri_to_key.get(str(agent_uri))
            for agent_uri in self.g.objects(step_uri, AGENTOSCIN.hasAssociatedAgent))), None),
        "aggregation_combinator": (
            self._str_value(step_uri, AGENTOSCIN.hasAggregationCombinator) or ""),
        # Per-step crew binding (callsCrew)
        "calls_crew": self._str_value(step_uri, CALLS_CREW),
    }
    step_uri_to_name[str(step_uri)] = name
