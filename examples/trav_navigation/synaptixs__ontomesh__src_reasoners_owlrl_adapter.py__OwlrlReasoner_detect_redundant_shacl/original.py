# Extracted from synaptixs/ontomesh@f771c8c4ee : src/reasoners/owlrl_adapter.py
# region: OwlrlReasoner.detect_redundant_shacl (lines 235-285, stratum trav_navigation)
# licence of the source repository: see meta.json
from typing import Iterable, List, Optional, Set, Tuple
from .base import Inconsistency, ReasonerResult, RedundancyFinding

def detect_redundant_shacl(self, ontology_path: str,
                           shapes_path: str,
                           ) -> List[RedundancyFinding]:
    if not self.available():
        return []
    try:
        import rdflib
    except ImportError:
        return []
    SH = rdflib.Namespace("http://www.w3.org/ns/shacl#")

    try:
        g = self._materialise(ontology_path)
    except Exception:                                           # noqa: BLE001
        return []
    try:
        shapes = rdflib.Graph()
        shapes.parse(shapes_path,
                     format=self._guess_format(shapes_path))
    except Exception:                                           # noqa: BLE001
        return []

    findings: List[RedundancyFinding] = []
    RDFS = rdflib.namespace.RDFS

    # Iterate sh:NodeShape entries.
    for shape in shapes.subjects(rdflib.namespace.RDF.type, SH.NodeShape):
        target_class = next(shapes.objects(shape, SH.targetClass), None)
        if target_class is None:
            continue
        # sh:property entries inside the shape.
        for prop_node in shapes.objects(shape, SH.property):
            path  = next(shapes.objects(prop_node, SH.path),  None)
            cls   = next(shapes.objects(prop_node, getattr(SH, "class")), None)
            if path is None or cls is None:
                continue
            # Is the SHACL claim "every <target_class>'s <path> is a
            # <cls>" already entailed by an rdfs:range declaration
            # in the closure?
            entailed_ranges = {str(o) for o in g.objects(path, RDFS.range)
                                if isinstance(o, rdflib.URIRef)}
            if str(cls) in entailed_ranges:
                findings.append(RedundancyFinding(
                    shape_iri=str(shape),
                    target_class=str(target_class),
                    constraint=f"sh:path={path} sh:class={cls}",
                    reason=(f"OWL entails rdfs:range({path}, {cls}); "
                            f"SHACL sh:class on this path is "
                            f"redundant."),
                ))
    return findings
