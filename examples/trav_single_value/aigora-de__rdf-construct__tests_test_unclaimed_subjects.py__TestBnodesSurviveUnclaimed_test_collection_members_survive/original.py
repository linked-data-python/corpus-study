# Extracted from aigora-de/rdf-construct@670e400ea4 : tests/test_unclaimed_subjects.py
# region: TestBnodesSurviveUnclaimed.test_collection_members_survive (lines 278-289, stratum trav_single_value)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import RDF, BNode, Graph, Literal, Namespace
from rdflib.namespace import OWL, RDFS
EX = Namespace("http://example.org/")

def test_collection_members_survive(
    self, restriction_ontology: Path, classes_only_config: Path, tmp_path: Path
) -> None:
    outdir = tmp_path / "out"
    assert _order(restriction_ontology, classes_only_config, outdir).exit_code == 0

    ordered = Graph()
    ordered.parse(outdir / "restrictions-classes_only.ttl")

    union = next(ordered.objects(EX.Union, OWL.unionOf))
    members = list(ordered.items(union))
    assert members == [EX.Dog, EX.Person]
