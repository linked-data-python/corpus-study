# Extracted from cognitedata/neat@4042d3e96d : tests/v0/tests_unit/test_rules/test_importers/test_inference_importer.py
# region: test_infer_with_bad_property_names (lines 132-151, stratum ns_import_project)
# licence of the source repository: see meta.json
import urllib.parse
from rdflib import RDF, Literal, Namespace
from cognite.neat._v0.core._constants import DEFAULT_NAMESPACE
from cognite.neat.legacy import NeatSession

def test_infer_with_bad_property_names() -> None:
    neat = NeatSession()
    neat._state.instances.store._add_triples(
        [
            (DEFAULT_NAMESPACE["MyAsset"], RDF.type, DEFAULT_NAMESPACE["Asset"]),
            (
                DEFAULT_NAMESPACE["MyAsset"],
                DEFAULT_NAMESPACE[urllib.parse.quote("My Property ill-formed")],
                Literal("My Value"),
            ),
        ],
        named_graph=neat._state.instances.store.default_named_graph,
    )
    neat.infer()
    assert neat._state.data_model_store.provenance
    info = neat._state.data_model_store.last_verified_conceptual_data_model

    assert info is not None
    assert len(info.properties) == 1
    assert info.properties[0].property_ == "myPropertyIllFormed"
