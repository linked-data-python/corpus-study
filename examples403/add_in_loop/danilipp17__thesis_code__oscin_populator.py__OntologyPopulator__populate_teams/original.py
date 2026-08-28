# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/populator.py
# region: OntologyPopulator._populate_teams (lines 698-703, stratum add_in_loop)
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

for kb_source in getattr(team, "knowledge_sources", []):
    kb_uri = self._create_individual(
        "KnowledgeBase", kb_source, AGENTO.KnowledgeBase
    )
    self._add_str(kb_uri, HAS_TITLE, kb_source)
    self.g.add((uri, AGENTO.hasKnowledge, kb_uri))
