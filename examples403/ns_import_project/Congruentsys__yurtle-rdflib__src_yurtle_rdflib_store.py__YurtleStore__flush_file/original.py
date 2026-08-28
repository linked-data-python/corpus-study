# Extracted from Congruentsys/yurtle-rdflib@8bbb378f5a : src/yurtle_rdflib/store.py
# region: YurtleStore._flush_file (lines 388-432, stratum ns_import_project)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import Graph, URIRef
from .core import (
    BEING,
    PM,
    YURTLE,
    YurtleDocument,
    YurtleParser,
    YurtleWriter,
)
from .namespaces import PROVENANCE
logger = logging.getLogger(__name__)

def _flush_file(self, path: Path) -> None:
    """
    Write a single file back to disk.

    Args:
        path: Path to the file to flush
    """
    logger.debug(f"Flushing file: {path}")

    state = self.file_states.get(path)
    if not state or not state.subject_uri:
        logger.warning(f"Cannot flush {path}: no state or subject URI")
        return

    # Collect all triples for this subject
    subject_graph = Graph()
    for prefix, ns in self.internal_graph.namespaces():
        subject_graph.bind(prefix, ns)

    for p, o in self.internal_graph.predicate_objects(state.subject_uri):
        # Skip provenance triples
        if p == PROVENANCE.definedIn:
            continue
        subject_graph.add((state.subject_uri, p, o))

    # Create YurtleDocument for serialization
    doc = YurtleDocument(
        graph=subject_graph,
        content=state.markdown_content,
        frontmatter_raw="",
        frontmatter_type="turtle",
        source_path=path,
        subject_uri=state.subject_uri,
    )

    # Write to file
    self.writer.write_file(doc, path)

    # Update state
    state.hash = self._compute_file_hash(path)
    state.last_modified = path.stat().st_mtime
    state.triple_count = len(subject_graph)
    state.is_dirty = False

    logger.debug(f"Flushed {path}: {state.triple_count} triples")
