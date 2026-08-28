# Extracted from mpsonntag/snippets@164fac3966 : python/odmlToRDF/subclassing.py
# region: test_rdf_subclassing_queries (lines 144-245, stratum bind_initbindings)
# licence of the source repository: see meta.json
import odml
from odml.tools import RDFWriter
from owlrl import DeductiveClosure, RDFS_Semantics
from rdflib.plugins.sparql import prepareQuery
NAMESPACE_MAP = {"odml": Namespace(ODML_NS), "rdf": RDF, "rdfs": RDFS}

def test_rdf_subclassing_queries():
    """
    Test the proper implementation of the RDF subclassing feature. Tests ensure, that queries
    relying on RDF Subclasses return appropriate results.
    """
    doc = odml.Document()
    _ = odml.Section(name="test_subclass", type="cell", parent=doc)
    _ = odml.Section(name="test_regular_class", type="regular", parent=doc)

    rdf_writer = RDFWriter([doc])
    _ = rdf_writer.get_rdf_str()

    use_graph = rdf_writer.graph
    DeductiveClosure(RDFS_Semantics).expand(use_graph)

    q_string = "SELECT * WHERE {?s rdf:type odml:Section .}"
    curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)

    # Make sure the query finds two sections
    assert len(use_graph.query(curr_query)) == 2

    # Make sure the query finds
    result_section = []
    for row in use_graph.query(curr_query):
        result_section.append(row.s)

    q_string = "SELECT * WHERE {?s rdf:type odml:Cell .}"
    curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)

    assert len(use_graph.query(curr_query)) == 1
    for row in use_graph.query(curr_query):
        assert row.s in result_section

    # -- Test custom subclassing queries
    type_custom_class = "species"
    type_overwrite_class = "cell"
    custom_class_dict = {type_custom_class: "Species", type_overwrite_class: "Neuron"}

    doc = odml.Document()
    sec = odml.Section(name="test_subclass", type="species", parent=doc)
    _ = odml.Section(name="test_subclass_overwrite", type="cell", parent=sec)
    _ = odml.Section(name="test_regular_class", type="regular", parent=sec)

    rdf_writer = RDFWriter([doc], custom_subclasses=custom_class_dict)
    _ = rdf_writer.get_rdf_str()

    use_graph = rdf_writer.graph
    DeductiveClosure(RDFS_Semantics).expand(use_graph)

    q_string = "SELECT * WHERE {?s rdf:type odml:Section .}"
    curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)

    # Make sure the query finds three sections
    assert len(use_graph.query(curr_query)) == 3

    # Make sure the query finds
    result_section = []
    for row in use_graph.query(curr_query):
        result_section.append(row.s)

    # Custom class 'Species' should be found.
    q_string = "SELECT * WHERE {?s rdf:type odml:Species .}"
    curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)

    assert len(use_graph.query(curr_query)) == 1
    for row in use_graph.query(curr_query):
        assert row.s in result_section

    # Custom class 'Neuron' should be found.
    q_string = "SELECT * WHERE {?s rdf:type odml:Neuron .}"
    curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)

    assert len(use_graph.query(curr_query)) == 1
    for row in use_graph.query(curr_query):
        assert row.s in result_section

    # Default class 'Cell' was replaced and should not return any result.
    q_string = "SELECT * WHERE {?s rdf:type odml:Cell .}"
    curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)

    assert not use_graph.query(curr_query)

    # -- Test inactivated subclassing
    doc = odml.Document()
    _ = odml.Section(name="test_regular_class", type="regular", parent=doc)
    _ = odml.Section(name="test_subclass", type="cell", parent=doc)

    rdf_writer = RDFWriter([doc], rdf_subclassing=False)
    _ = rdf_writer.get_rdf_str()

    use_graph = rdf_writer.graph
    DeductiveClosure(RDFS_Semantics).expand(use_graph)

    q_string = "SELECT * WHERE {?s rdf:type odml:Section .}"
    curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)

    assert len(use_graph.query(curr_query)) == 2

    q_string = "SELECT * WHERE {?s rdf:type odml:Cell .}"
    curr_query = prepareQuery(q_string, initNs=NAMESPACE_MAP)

    assert not use_graph.query(curr_query)
