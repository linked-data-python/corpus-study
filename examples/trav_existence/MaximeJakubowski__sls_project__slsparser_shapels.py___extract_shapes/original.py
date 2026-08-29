# Extracted from MaximeJakubowski/sls_project@58f7d7840f : slsparser/shapels.py
# region: _extract_shapes (lines 83-119, stratum trav_existence)
# licence of the source repository: see meta.json
from typing import Dict, List, Optional, Tuple, Set
from rdflib import Graph
from rdflib import SH, RDF, RDFS
from rdflib.term import URIRef, Literal, BNode, Node
from rdflib.collection import Collection

def _extract_shapes(graph: Graph) -> Set[Node]:
    # A shape is:
    # - instance of NodeShape or PropertyShape
    # - subject of targetClass, target...
    # - subject of any constraint component parameter
    # - object of a constraint component parameter that expects a shape

    # parameters whose object is (or may be) a shape
    object_parameters = [SH.property, SH.node, SH.qualifiedValueShape, SH['not']]

    # parameters whose subject is a shape (constraint components and targets)
    subject_parameters = [
        SH.node, SH.qualifiedValueShape, SH.qualifiedMinCount, SH.qualifiedMaxCount,
        SH['not'], SH['class'], SH.datatype, SH.nodeKind, SH.minCount, SH.maxCount,
        SH.minExclusive, SH.minInclusive, SH.maxExclusive, SH.maxInclusive,
        SH.minLength, SH.maxLength, SH.pattern, SH.languageIn, SH.uniqueLang,
        SH.equals, SH.disjoint, SH.lessThan, SH.lessThanOrEquals, SH.closed,
        SH.hasValue, SH.targetClass, SH.targetNode, SH.targetObjectsOf,
        SH.targetSubjectsOf, SH.property,
    ]

    shapes: Set[Node] = set()
    for parameter in object_parameters:
        shapes.update(graph.objects(predicate=parameter))
    for parameter in subject_parameters:
        shapes.update(graph.subjects(predicate=parameter))
    shapes.update(graph.subjects(RDF.type, SH.NodeShape))
    shapes.update(graph.subjects(RDF.type, SH.PropertyShape))

    # also members of a shacl list which are objects of sh:and, sh:or, sh:xone
    for parameter in [SH['or'], SH['and'], SH.xone]:
        for llist in graph.objects(predicate=parameter):
            for shapename in Collection(graph, llist):
                if SH.path not in graph.predicates(shapename):
                    shapes.add(shapename)

    return shapes
