# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/nodesetparser.py
# region: NodesetParser.add_semantic_bridge (lines 260-289, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef, BNode
import urllib
attribute_prefix = utils.ATTRIBUTE_PREFIX

def add_semantic_bridge(self):
    """Add semantic relationships to the graph.

    This function executes a SPARQL query to find all semantic relationships and adds them to the graph.

    """
    not_needed_property_query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?s ?sbc ?o ?bn ?nsuri WHERE {
        ?sbc rdfs:subPropertyOf* opcua:Aggregates .
        ?s ?sbc ?o .
        ?o base:hasBrowseName ?bn .
        ?o base:hasBrowseNameNamespace ?bnn .
        ?bnn base:hasUri ?nsuri .
    }
    """
    joint_graph = self.g + self.ig
    root_property = self.rdf_utils.get_root_property_of_semantic_bridge()
    bindings = {'root_property': root_property}
    query_result = joint_graph.query(not_needed_property_query, initNs=self.rdf_ns, initBindings=bindings)
    for s, sbc, o, bn, nsuri in query_result:
        if ((s, sbc, o) in self.g) is False:
            continue
        targetns = Namespace(str(nsuri))
        targetreference = targetns[urllib.parse.quote(f'{attribute_prefix}{bn}')]
        self.g.add((s, targetreference, o))
        self.add_semantic_relationship(targetreference)
