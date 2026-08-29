# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/utils.py
# region: RdfUtils.get_all_subreferences (lines 868-892, stratum bind_initbindings)
# licence of the source repository: see meta.json
def get_all_subreferences(self, graph, node, reference):
    """Get non-hierarchical references

    Args:
        graph (Graph)): Graph to search in
        node (URIRef): Node to start searching
        reference (URIRef): Reference superclass

    Returns:
        list(URIRef): List of References found for the node
    """
    query_generic_references = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    select ?reference ?target where {
        ?node ?reference ?target .
        ?reference rdfs:subPropertyOf* ?superclass .
    }
    """
    bindings = {'node': node, 'superclass': reference}
    result = graph.query(query_generic_references, initBindings=bindings, initNs={'opcua': self.opcuans})
    results = []
    if len(result) > 0:
        results = list(result)
    return results
