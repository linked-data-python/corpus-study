# Extracted from Congruentsys/yurtle-rdflib@8bbb378f5a : src/yurtle_rdflib/store.py
# region: YurtleStore.remove (lines 534-561, stratum remove)
# licence of the source repository: see meta.json
from typing import Any
from rdflib import Graph, URIRef
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
    s, p, o = triple

    # Find all matching triples first
    matching = list(self.internal_graph.triples((s, p, o)))

    for match_s, match_p, match_o in matching:
        self.internal_graph.remove((match_s, match_p, match_o))

        # Mark affected file as dirty
        if isinstance(match_s, URIRef):
            target_file = self._resolve_file_for_subject(match_s)
            if target_file:
                self._mark_file_dirty(target_file)

    if self.auto_flush and self._dirty_files:
        self.flush()
