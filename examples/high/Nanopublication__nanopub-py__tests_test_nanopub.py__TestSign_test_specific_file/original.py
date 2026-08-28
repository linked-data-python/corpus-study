# Extracted from Nanopublication/nanopub-py@05022dc4bc : tests/test_nanopub.py
# region: TestSign.test_specific_file (lines 616-663, band high)
# licence of the source repository: see meta.json
import json
from rdflib import BNode, Graph, Literal, URIRef, Dataset, DC, RDF, Namespace, DCTERMS, PROV, XSD
from nanopub import (
    Nanopub,
    NanopubConf,
    namespaces,
)
from tests.conftest import (
    default_conf,
    profile_test,
    skip_if_nanopub_server_unavailable, testsuite, testsuite_conf,
)

def test_specific_file(self):
    """Test to sign a complex file with many blank nodes"""

    np_conf = NanopubConf(profile=profile_test, use_test_server=True)
    np_conf.add_prov_generated_time = (True,)
    np_conf.add_pubinfo_generated_time = (True,)
    np_conf.attribute_assertion_to_profile = (True,)
    np_conf.attribute_publication_to_profile = (True,)

    with open("./tests/resources/many_bnodes_with_annotations.json") as f:
        nanopub_rdf = json.loads(f.read())

    annotations_rdf = nanopub_rdf["@annotations"]
    del nanopub_rdf["@annotations"]
    nanopub_rdf = str(json.dumps(nanopub_rdf))

    g = Graph()
    g.parse(data=nanopub_rdf, format="json-ld")

    np = Nanopub(
        assertion=g,
        conf=np_conf,
    )
    source = "https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=f9641190-9151-4f7e-89ff-1e7a818c30ee"
    if annotations_rdf:
        np.provenance.parse(data=str(json.dumps(annotations_rdf)), format="json-ld")
    if source:
        np.provenance.add(
            (np.assertion.identifier, PROV.hadPrimarySource, URIRef(source))
        )

    PAV = Namespace("http://purl.org/pav/")
    if True:
        np.pubinfo.add(
            (
                np.metadata.np_uri,
                DCTERMS.conformsTo,
                URIRef("https://w3id.org/biolink/vocab/"),
            )
        )
        np.pubinfo.add(
            (
                URIRef("https://w3id.org/biolink/vocab/"),
                PAV.version,
                Literal("3.1.0"),
            )
        )
    np.sign()
