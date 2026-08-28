# Extracted from danilipp17/thesis_code@c2772e3555 : oscin/reader.py
# region: OntologyReader._read_tasks (lines 380-382, stratum trav_navigation)
# licence of the source repository: see meta.json
from oscin.namespaces import (
    AGENTO,
    AGENTOSCIN,
    CALLS_CREW,
    COORD_CUSTOM,
    COORD_SEQUENTIAL,
    HAS_DESCRIPTION,
    HAS_TITLE,
)

human_input = bool(
    list(self.g.objects(task_uri, AGENTOSCIN.hasHumanCheckpoint))
)
