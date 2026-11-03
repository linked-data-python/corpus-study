# Extracted from Congruentsys/yurtle-rdflib@8bbb378f5a : src/yurtle_rdflib/store.py
# region: YurtleStore.remove (lines 534-561, stratum remove)
# licence of the source repository: see meta.json
from typing import Any
from rdflib import URIRef
from rdflib.term import Node

def remove(
    self,
    triple: tuple[Node | None, Node | None, Node | None],
    context: Any = None,
) -> None:
    """
    Remove triples matching the pattern.

    Args:
        triple: (subject, predicate, object) with None as wildcard
        context: Graph context (unused)
    """
    # Find all matching triples first
    for match in list(self.internal_graph.triples(triple)):
        self.internal_graph.remove(match)

        # Mark affected file as dirty
        if isinstance(match[0], URIRef):
            target_file = self._resolve_file_for_subject(match[0])
            if target_file:
                self._mark_file_dirty(target_file)

    if self.auto_flush and self._dirty_files:
        self.flush()
