# Extracted from linkml/linkml@680595df54 : tests/linkml/test_generators/test_shaclgen.py
# region: test_nodeshape_uses_rdfs_predicates (lines 790-828, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
from rdflib import RDF, RDFS, SH, Literal, URIRef
from linkml.generators.shaclgen import ShaclGenerator

def test_nodeshape_uses_rdfs_predicates(kitchen_sink_path):
    """Test that NodeShapes use rdfs:label and rdfs:comment, not sh:name and sh:description.

    Per the SHACL spec, sh:name and sh:description both have rdfs:domain of sh:PropertyShape,
    so using them on NodeShapes causes RDFS-aware validators to incorrectly infer the
    NodeShape is also a PropertyShape. See issue #3059.
    """
    shacl = ShaclGenerator(kitchen_sink_path, mergeimports=True).serialize()
    g = rdflib.Graph()
    g.parse(data=shacl)

    person_uri = URIRef("https://w3id.org/linkml/tests/kitchen_sink/Person")

    # Verify Person is a NodeShape
    assert (person_uri, RDF.type, SH.NodeShape) in g

    # Verify NodeShape uses rdfs:comment for its description (not sh:description)
    nodeshape_comments = list(g.objects(person_uri, RDFS.comment))
    assert len(nodeshape_comments) == 1
    assert "person" in str(nodeshape_comments[0]).lower()

    # Verify NodeShape does NOT have sh:description (this was the bug)
    nodeshape_sh_descriptions = list(g.objects(person_uri, SH.description))
    assert len(nodeshape_sh_descriptions) == 0, "NodeShapes should not use sh:description; use rdfs:comment instead"

    # Verify no NodeShape has sh:name (sh:name also has rdfs:domain sh:PropertyShape)
    for node_shape in g.subjects(RDF.type, SH.NodeShape):
        sh_names = list(g.objects(node_shape, SH.name))
        assert len(sh_names) == 0, f"NodeShape {node_shape} should not use sh:name; use rdfs:label instead"

    # Verify PropertyShapes still use sh:description (this is correct per spec)
    # Check that at least one property shape (BNode) uses sh:description
    found_property_description = False
    for prop_shape in g.subjects(SH.description, None):
        # Property shapes are blank nodes, NodeShapes are URIs
        if isinstance(prop_shape, rdflib.BNode):
            found_property_description = True
            break
    assert found_property_description, "PropertyShapes should use sh:description"
