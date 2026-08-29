# Extracted from fair-workflows/fairworkflows@363a759032 : fairworkflows/fairworkflow.py
# region: FairWorkflow._get_relevant_triples (lines 155-178, stratum bind_initbindings)
# licence of the source repository: see meta.json
import rdflib

@staticmethod
def _get_relevant_triples(uri, rdf):
    """
    Select only relevant triples from RDF using the following heuristics:
    * Match all triples that are through an arbitrary-length property path related to the
        workflow uri. So if 'URI predicate Something', then all triples 'Something predicate
        object' are selected, and so forth.
    NB: We assume that all step-related triples are already extracted by the _extract_steps
    method
    """
    q = """
    CONSTRUCT { ?s ?p ?o }
    WHERE {
        ?s ?p ?o .
        # Match all triples that are through an arbitrary-length property path related to the
        # workflow uri. (<>|!<>) matches all predicates. Binding to workflow_uri is done when
        # executing.
        ?workflow_uri (<>|!<>)* ?s .
    }
    """
    g = rdflib.Graph(namespace_manager=rdf.namespace_manager)
    for triple in rdf.query(q, initBindings={'workflow_uri': rdflib.URIRef(uri)}):
        g.add(triple)
    return g
