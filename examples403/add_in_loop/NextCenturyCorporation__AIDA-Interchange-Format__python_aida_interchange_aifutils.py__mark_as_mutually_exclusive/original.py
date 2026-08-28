# Extracted from NextCenturyCorporation/AIDA-Interchange-Format@1197e7adef : python/aida_interchange/aifutils.py
# region: mark_as_mutually_exclusive (lines 779-820, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import RDF, XSD, BNode, Graph, Literal, URIRef
from aida_interchange.rdf_ontologies import interchange_ontology

def mark_as_mutually_exclusive(g, alternatives, system, none_of_the_above_prob):
    """
    Mark the given resources as mutually exclusive.

    This is a special case of [mark_as_mutually_exclusive] where the alternatives are
    each single edges, so we simply wrap each edge in a collection and pass to
    mark_as_mutually_exclusive.

    :param rdflib.graph.Graph g: The underlying RDF model
    :param dict alternatives: a dictionary of edges which form a sub-graph for
        an alternative to the confidence associated with an alternative.
    :param rdflib.term.URIRef system: The system object for the system which contains the
        mutual exclusion
    :param float none_of_the_above_prob: if not None, the given confidence will be applied for
        the "none of the above" option.
    :returns: The created mutual exclusion assertion resource
    :rtype: rdflib.term.BNode
    """
    if len(alternatives) < 2:
        raise RuntimeError("alternatives cannot have less than 2 mutually exclusive things")

    mutual_exclusion_assertion = _make_aif_resource(g, None, interchange_ontology.MutualExclusion, system)

    for (edges_for_alternative, confidence) in alternatives.items():
        alternative = BNode()
        g.add((alternative, RDF.type, interchange_ontology.MutualExclusionAlternative))

        alternative_graph = BNode()
        g.add((alternative_graph, RDF.type, interchange_ontology.Subgraph))
        for alt in edges_for_alternative:
            g.add((alternative_graph, interchange_ontology.subgraphContains, alt))

        g.add((alternative, interchange_ontology.alternativeGraph, alternative_graph))
        mark_confidence(g, alternative, confidence, system)

        g.add((mutual_exclusion_assertion, interchange_ontology.alternative, alternative))

    if none_of_the_above_prob is not None:
        g.add((mutual_exclusion_assertion, interchange_ontology.noneOfTheAbove,
               Literal(none_of_the_above_prob, datatype=XSD.double)))

    return mutual_exclusion_assertion
