# Extracted from unibz-core/Scior@1d9f010224 : scior/modules/ontology_dataclassess/dataclass_initialization.py
# region: get_known_gufo_individuals (lines 151-179, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph
from scior.modules.resources_gufo import GUFO_NAMESPACE, GUFO_LIST_ENDURANT_TYPES

def get_known_gufo_individuals(united_graph: Graph) -> list[tuple]:
    """ For each class in the ontology_graph, return all its known GUFO INDIVIDUALS in a tuple format.
    Returned tuple format is: (ontology_class,gufo_type), being both fields strings.
    Analogous to get_known_gufo_types.
    """

    list_elements = []
    list_individuals = []

    query_string = """
        PREFIX gufo: <http://purl.org/nemo/gufo#>
        SELECT DISTINCT ?ontology_element ?element_type
        WHERE {
            ?ontology_element rdf:type owl:Class .
            ?element_type rdf:type owl:Class .
            ?ontology_element rdfs:subClassOf ?element_type .
            ?element_type rdfs:subClassOf+ gufo:Endurant .
            FILTER(STRSTARTS(STR(?element_type), STR(gufo:)))
        } """

    query_result = united_graph.query(query_string)

    for row in query_result:
        list_elements.append(row.ontology_element.toPython())
        list_individuals.append(row.element_type.toPython().replace(GUFO_NAMESPACE, ""))

    list_tuples = list(zip(list_elements, list_individuals))

    return list_tuples
