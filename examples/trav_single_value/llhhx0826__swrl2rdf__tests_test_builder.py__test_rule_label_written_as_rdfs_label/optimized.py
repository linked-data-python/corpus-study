# Extracted from llhhx0826/swrl2rdf@190ffb3068 : tests/test_builder.py
# region: test_rule_label_written_as_rdfs_label (lines 40-49, stratum trav_single_value)
# licence of the source repository: see meta.json
#
# swrl2rdf is not an installable dependency here: imports of
# swrl2rdf.builder/model/prefixmap replaced by swrl2rdf_shim (see meta.json),
# a verbatim subset of those three modules. Nothing else changed.
from rdflib.namespace import Namespace, RDF, RDFS
from swrl2rdf_shim import rules_to_graph
from swrl2rdf_shim import ClassAtom, Rule, SameIndividualAtom, Variable
from swrl2rdf_shim import PrefixMap
SWRL = Namespace("http://www.w3.org/2003/11/swrl#")
EX = "http://example.org/"

def test_rule_label_written_as_rdfs_label(prefix_map: PrefixMap) -> None:
    """Rule labels must be stored as rdfs:label on the swrl:Imp."""
    g = rules_to_graph([Rule(
        label="Rule_0",
        body=[ClassAtom(class_predicate=EX + "Person", argument=Variable("p"))],
        head=[ClassAtom(class_predicate=EX + "Adult", argument=Variable("p"))],
    )], prefix_map)
    imp = next(g.subjects(RDF.type, SWRL.Imp))
    assert str(g.value(imp, RDFS.label)) == "Rule_0"
