# Extracted from INCATools/kgcl-rdflib@7af638bbd7 : kgcl_rdflib/diff/owlstar_sublanguage.py
# region: get_bnodes_2_triple_annotations (lines 303-343, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import BNode
from rdflib.namespace import OWL, RDF, RDFS

def get_bnodes_2_triple_annotations(g):
    """Get blank nodes to triple annotations."""
    source = set(g.subjects(predicate=OWL.annotatedSource))
    property = set(g.subjects(predicate=OWL.annotatedProperty))
    target = set(g.subjects(predicate=OWL.annotatedTarget))

    # get blank nodes that have all three required predicates
    intersection = source & property & target

    exclude = {
        OWL.annotatedSource,
        OWL.annotatedProperty,
        OWL.annotatedTarget,
        # RDF.type,
    }

    annotations = {}
    for i in intersection:
        annotations[i] = []
        if isinstance(i, BNode):  # this check should be unnecessary
            # NB these generators are singletons
            source = next(g.objects(subject=i, predicate=OWL.annotatedSource))
            property = next(g.objects(subject=i, predicate=OWL.annotatedProperty))
            target = next(g.objects(subject=i, predicate=OWL.annotatedTarget))

            annotations[i].append((i, OWL.annotatedSource, source))
            annotations[i].append((i, OWL.annotatedProperty, property))
            annotations[i].append((i, OWL.annotatedTarget, target))

            for s, p, o in g.triples((i, None, None)):
                if (
                    p not in exclude
                    and not isinstance(o, BNode)
                    and not isinstance(p, BNode)
                    and not isinstance(source, BNode)
                    and not isinstance(property, BNode)
                    and not isinstance(target, BNode)
                ):
                    annotations[i].append((s, p, o))

    return annotations
