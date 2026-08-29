# Extracted from unibz-core/Scior@1d9f010224 : scior/modules/rules/rule_group_ufo_some.py
# region: run_rs08 (lines 553-611, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, RDFS
from scior.modules.ontology_dataclassess.dataclass_definitions import OntologyDataClass
from scior.modules.problems_treatment.treat_incomplete import IncompletenessEntry, register_incompleteness
from scior.modules.utils_dataclass import get_dataclass_by_uri
LOGGER = initialize_logger()

def run_rs08(ontology_dataclass_list: list[OntologyDataClass], ontology_graph: Graph,
             incompleteness_stack: list[IncompletenessEntry]) -> None:
    """ Executes rule RS08 from group UFO Some.

    Definition: PhaseMixin(x) -> E y (Category (y) ^ isSubClassOf(x,y))
    Description: Every PhaseMixin specializes at least one Category.

    :param ontology_dataclass_list: List with all OntologyDataClass elements, including their URIs and internal lists.
    :type ontology_dataclass_list: list[OntologyDataClass]
    :param ontology_graph: Updated ontology's working (RDFLib) graph on memory to be manipulated.
    :type ontology_graph: Graph
    :param incompleteness_stack: List of identified incompleteness to be updated if necessary.
    :type incompleteness_stack: list[IncompletenessEntry]
    """

    rule_code = "RS08"

    LOGGER.debug(f"Starting rule {rule_code}")

    query_string = """
        PREFIX gufo: <http://purl.org/nemo/gufo#>
        SELECT DISTINCT ?class_x ?class_y
        WHERE {
            ?class_x rdf:type gufo:PhaseMixin .
            ?class_x rdfs:subClassOf ?class_y .
        } """

    query_result = ontology_graph.query(query_string)
    is_dictionary = {}
    can_dictionary = {}

    for row in query_result:

        # Class to be completed or that may be incomplete
        evaluated_class = row.class_x.toPython()
        # Class that may be used to complete the evaluated_dataclass
        selected_class = row.class_y.toPython()

        # If evaluated_class not in dictionary yet, create it
        if evaluated_class not in is_dictionary.keys():
            is_dictionary[evaluated_class] = []
            can_dictionary[evaluated_class] = []

        selected_dataclass = get_dataclass_by_uri(ontology_dataclass_list, selected_class)

        # Creating IS List
        if "Category" in selected_dataclass.is_type:
            is_dictionary[evaluated_class].append(selected_class)

        # Creating CAN List
        elif "Category" in selected_dataclass.can_type:
            can_dictionary[evaluated_class].append(selected_class)

    for evaluated in is_dictionary.keys():
        evaluated_dataclass = get_dataclass_by_uri(ontology_dataclass_list, evaluated)
        treat_result_ufo_some(ontology_dataclass_list, evaluated_dataclass, can_dictionary[evaluated],
                              is_dictionary[evaluated], ["Category"], rule_code, incompleteness_stack)

    LOGGER.debug(f"Rule {rule_code} concluded.")
