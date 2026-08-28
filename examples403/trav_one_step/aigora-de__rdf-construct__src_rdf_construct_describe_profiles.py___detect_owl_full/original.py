# Extracted from aigora-de/rdf-construct@670e400ea4 : src/rdf_construct/describe/profiles.py
# region: _detect_owl_full (lines 175-230, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, RDF, RDFS, URIRef
from rdflib.namespace import OWL, XSD

def _detect_owl_full(graph: Graph) -> list[str]:
    """Detect constructs that indicate OWL Full.

    OWL Full allows patterns that are undecidable, including:
    - Metaclasses (classes that are instances of other classes)
    - Properties with classes as values
    - Circular definitions in certain ways

    Args:
        graph: RDF graph to analyse.

    Returns:
        List of OWL Full indicator descriptions.
    """
    issues: list[str] = []

    # Check for metaclasses: classes that are rdf:type of other classes
    # This is a common OWL Full pattern
    owl_classes = set(graph.subjects(RDF.type, OWL.Class))
    rdfs_classes = set(graph.subjects(RDF.type, RDFS.Class))
    all_classes = owl_classes | rdfs_classes

    for cls in all_classes:
        # Check if this class is an instance of another class (not owl:Class/rdfs:Class)
        for class_type in graph.objects(cls, RDF.type):
            if class_type not in {OWL.Class, RDFS.Class} and class_type in all_classes:
                issues.append(
                    f"Metaclass: {_curie(graph, cls)} is instance of class {_curie(graph, class_type)}"
                )

    # Check for owl:Class used in unexpected positions
    # For example, as the object of a property that expects individuals
    for s, p, o in graph:
        # Skip type assertions
        if p == RDF.type:
            continue

        # If object is a class and predicate domain/range suggests individuals
        if o in all_classes:
            # Check if predicate is an object property with individual range
            if (p, RDF.type, OWL.ObjectProperty) in graph:
                prop_range = list(graph.objects(p, RDFS.range))
                # If range is defined and is not a class of classes, this might be Full
                # This is a simplified check; full analysis would require more inference

    # Check for problematic self-reference patterns
    # e.g., C owl:equivalentClass [ owl:complementOf C ] could be problematic
    for cls in owl_classes:
        equiv_classes = list(graph.objects(cls, OWL.equivalentClass))
        for equiv in equiv_classes:
            # Check for direct self-equivalence to complement
            complement = list(graph.objects(equiv, OWL.complementOf))
            if cls in complement:
                issues.append(f"Self-contradictory equivalence: {_curie(graph, cls)}")

    return issues
