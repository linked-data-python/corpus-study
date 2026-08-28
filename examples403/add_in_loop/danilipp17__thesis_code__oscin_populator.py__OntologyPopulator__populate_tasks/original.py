# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/populator.py
# region: OntologyPopulator._populate_tasks (lines 427-429, stratum add_in_loop)
# licence of the source repository: see meta.json
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

for tool_name in task.tools:
    tool_uri = self._resolve_or_create_tool(tool_name)
    self.g.add((uri, AGENTOSCIN.taskToolUsage, tool_uri))
