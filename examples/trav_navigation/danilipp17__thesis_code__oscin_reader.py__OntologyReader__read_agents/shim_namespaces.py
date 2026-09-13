# Context shim (see meta.json): subset of oscin/namespaces.py from
# danilipp17/thesis_code@c2772e3555, so the region executes outside the
# package. Identical bindings for both representations.
from rdflib import Namespace

AGENTOSCIN = Namespace(
    "http://www.semanticweb.org/danilippmann/ontologies/2026/3/agentoscin/"
)
AGENTO = Namespace("http://www.w3id.org/agentic-ai/onto#")
HAS_TITLE = AGENTOSCIN.hasTitle
HAS_DESCRIPTION = AGENTOSCIN.hasDescription
CALLS_CREW = AGENTOSCIN.callsCrew
COORD_SEQUENTIAL = AGENTOSCIN["Sequential"]
COORD_CUSTOM = AGENTOSCIN["Custom"]
