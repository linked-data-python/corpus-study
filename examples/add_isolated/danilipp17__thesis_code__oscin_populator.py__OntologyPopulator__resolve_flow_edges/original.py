# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/populator.py
# region: OntologyPopulator._resolve_flow_edges (lines 946-1015, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD
from oscin.namespaces import (
    AGENTO,
    AGENTOSCIN,
    CALLS_CREW,
    COORD_CUSTOM,
    COORD_HIERARCHICAL,
    COORD_NETWORK,
    COORD_REACT_LOOP,
    COORD_ROUND_ROBIN,
    COORD_SELECTOR_BASED,
    COORD_SEQUENTIAL,
    COORD_SWARM,
    HAS_DESCRIPTION,
    HAS_REFERENCE,
    HAS_TITLE,
    make_instance_namespace,
)

def _resolve_flow_edges(
    self, flow, step_uris: dict[str, URIRef], outgoing_edges: dict[str, list[str]],
    conditional_step_names: set[str] | None = None,
) -> None:
    # Resolve target mapping: @listen("label") or method names
    # First pass: map step names to their own URIs
    label_map: dict[str, URIRef] = {}
    for step in flow.steps:
        label_map[step.method_name] = step_uris[step.method_name]
    # Second pass: add listener labels (only if not already mapped)
    # This handles CrewAI @listen("label") patterns without
    # overriding step_name → URI mappings needed by LangGraph.
    for step in flow.steps:
        if step.step_type in ("listen", "regular", "start"):
            for arg in step.dependencies:
                if arg not in label_map:
                    label_map[arg] = step_uris[step.method_name]

    # Connect edges
    for step in flow.steps:
        src_uri = step_uris[step.method_name]

        # Direct outgoing edges recorded by the parser (e.g. LangGraph
        # add_edge("a","b") incl. back-edges that close ReAct loops).
        # rdflib dedupes triples, so this is safe even if a later branch
        # adds the same edge again.
        for tgt in step.outgoing:
            if tgt in label_map:
                self.g.add((src_uri, AGENTO.nextStep, label_map[tgt]))
                outgoing_edges[step.method_name].append(tgt)

        # Steps with return_values (routers, or start nodes with
        # conditional edges in LangGraph)
        if step.return_values:
            for ret_val in step.return_values:
                if ret_val in label_map:
                    self.g.add((src_uri, AGENTO.nextStep, label_map[ret_val]))
                    outgoing_edges[step.method_name].append(ret_val)

        # For any step (not just start), create nextStep edges to steps
        # whose dependencies reference this step by method name.
        # This captures @listen(method) and @router(method) patterns.
        if not step.return_values:
            for other in flow.steps:
                if other.method_name == step.method_name:
                    continue
                if any(arg == step.method_name for arg in other.dependencies):
                    self.g.add(
                        (
                            src_uri,
                            AGENTO.nextStep,
                            step_uris[other.method_name],
                        )
                    )
                    outgoing_edges[step.method_name].append(other.method_name)

    # Reclassify dead-ends as EndSteps (keep WorkflowStep as parent type).
    # Skip conditional/router steps — they may have zero resolved edges
    # because their routing targets didn't map to step URIs, but they
    # are NOT terminal steps.
    # Also skip steps that are already StartSteps — a start node
    # cannot also be a terminal node in a non-trivial flow.
    conditional = conditional_step_names or set()
    start_step_names = {
        s.method_name for s in flow.steps if s.step_type == "start"
    }
    for step_name, edges in outgoing_edges.items():
        if not edges and step_name not in conditional and step_name not in start_step_names:
            uri = step_uris[step_name]
            self.g.add((uri, RDF.type, AGENTO.EndStep))
