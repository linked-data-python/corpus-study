# Context shim (see meta.json): subset of kgraphpy/header.py from
# statnett/KGraphPy@38859be62fdc2fd048e3ad1651bc16f0dcabaf75, so the region
# executes outside the package. Identical bindings for both representations.
# Only the path the test exercises is kept: __init__, from_graph,
# _collect_header_triples and _repair_blank_header_subject.
from rdflib import Graph, Node, URIRef, RDF, BNode, Literal
from rdflib.namespace import DCTERMS, NamespaceManager
from kgraphpy.namespaces import MD, collect_specific_namespaces
from typing import Iterable, List, Tuple, Optional, Set
import logging
import uuid

logger = logging.getLogger("cimxml_logger")


class CIMMetadataHeader:
    """Represents the CIMXML metadata header extracted from a Graph."""

    DEFAULT_METADATA_OBJECTS: Set[URIRef] = set()
    DEFAULT_PROFILE_PREDICATES: Set[URIRef] = {
        MD.Model.profile,
        DCTERMS.conformsTo,
    }

    def __init__(
        self,
        subject: Optional[URIRef] = None,
        graph: Optional[Graph] = None,
        metadata_objects: Optional[Iterable[URIRef]] = None,
        reachable_nodes: Optional[Set[Node]] = None,
        profile_predicates: Optional[Set[URIRef]] = None,
    ):
        if subject is None:
            subject = URIRef(f"urn:uuid:{uuid.uuid4()}")

        self.subject: URIRef = subject
        self.graph: Graph = graph if graph is not None else Graph()

        self.metadata_objects = (
            set(metadata_objects)
            if metadata_objects
            else set(self.DEFAULT_METADATA_OBJECTS)
        )

        self.reachable_nodes: Set[Node] = reachable_nodes or set()
        self.profile_predicates = profile_predicates or self.DEFAULT_PROFILE_PREDICATES

    @classmethod
    def from_graph(
        cls, graph: Graph, metadata_objects: Optional[Iterable[URIRef]] = None
    ) -> "CIMMetadataHeader":
        """Extract the metadata header from a graph."""

        metadata_objects = (
            list(metadata_objects)
            if metadata_objects
            else list(cls.DEFAULT_METADATA_OBJECTS)
        )

        header_subjects = [
            s
            for (s, _, o) in graph.triples((None, RDF.type, None))
            if o in metadata_objects
        ]

        if not header_subjects:
            raise ValueError("No metadata header found in graph")

        if len(header_subjects) > 1:
            raise ValueError(f"Multiple metadata headers found: {header_subjects}")

        header_subject = header_subjects[0]

        final_subject, repaired_triples, reachable = cls._collect_header_triples(
            graph, header_subject
        )

        header_graph = Graph()
        for triple in repaired_triples:
            header_graph.add(triple)

        nm = NamespaceManager(header_graph, bind_namespaces="none")
        used_namespaces = collect_specific_namespaces(repaired_triples, graph.namespace_manager)
        for prefix, ns_uri in used_namespaces.items():
            nm.bind(prefix, ns_uri, override=True)

        header_graph.namespace_manager = nm

        return cls(
            subject=final_subject,
            graph=header_graph,
            metadata_objects=metadata_objects,
            reachable_nodes=reachable,
        )

    @classmethod
    def _collect_header_triples(
        cls, graph: Graph, header_subject: Node
    ) -> Tuple[URIRef, List[Tuple[Node, Node, Node]], Set[Node]]:
        """Collect all triples reachable from the header subject."""
        reachable: Set[Node] = set()
        queue: List[Node] = [header_subject]

        while queue:
            current = queue.pop()
            if current in reachable:
                continue

            reachable.add(current)

            for (_, _, obj) in graph.triples((current, None, None)):
                if isinstance(obj, BNode) and obj not in reachable:
                    queue.append(obj)

        collected: List[Tuple[Node, Node, Node]] = []
        for s in reachable:
            for triple in graph.triples((s, None, None)):
                collected.append(triple)

        if isinstance(header_subject, URIRef):
            final_subject = header_subject
        else:
            final_subject = cls._repair_blank_header_subject(graph, header_subject)

        repaired: List[Tuple[Node, Node, Node]] = []
        for (s, p, o) in collected:
            if isinstance(o, BNode):
                continue
            if isinstance(s, BNode):
                repaired.append((final_subject, p, o))
            else:
                repaired.append((s, p, o))

        return final_subject, repaired, reachable

    @classmethod
    def empty(
        cls,
        subject: Optional[URIRef] = None,
        metadata_objects: Optional[Iterable[URIRef]] = None,
        profile_predicates: Optional[Set[URIRef]] = None,
    ):
        g = Graph()
        return cls(
            subject=subject,
            graph=g,
            metadata_objects=metadata_objects,
            profile_predicates=profile_predicates,
        )

    @staticmethod
    def _repair_blank_header_subject(graph: Graph, blank: Node) -> URIRef:
        """Repair header subject by turning it into a uuid uri."""
        logger.error(
            f"Metadata header subject is a blank node ({blank}). "
            "Attempting to collect subject from dcterms:identifier."
        )

        for (_, _, identifier) in graph.triples((blank, DCTERMS.identifier, None)):
            if identifier and isinstance(identifier, Literal):
                return URIRef(f"urn:uuid:{identifier.toPython()}")

        new_id = uuid.uuid4()
        logger.error(
            f"No dcterms:identifier found for blank header subject. "
            f"Random UUID generated: {new_id}"
        )
        return URIRef(f"urn:uuid:{new_id}")


def create_header_attribute(graph: Graph) -> CIMMetadataHeader:
    """Create a header from a graph."""
    try:
        header = CIMMetadataHeader.from_graph(graph)
    except ValueError as e:
        header = CIMMetadataHeader.empty()
        logger.error(f"{e}: Random id generated for graph: {str(header.subject)}")

    return header
