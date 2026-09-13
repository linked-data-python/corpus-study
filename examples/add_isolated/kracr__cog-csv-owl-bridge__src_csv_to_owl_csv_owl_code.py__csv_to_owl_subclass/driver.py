"""Validation driver for
kracr__cog-csv-owl-bridge__src_csv_to_owl_csv_owl_code.py__csv_to_owl_subclass.

Establishes semantic equivalence of original.py and translated.ldpy.

csv_to_owl_subclass's whole observable effect is the OWL file it serializes
-- it takes no graph argument to mutate and returns nothing -- so
``run_pair(entry=...)`` alone would only ever compare the (trivially equal)
string arguments: a hollow green. Instead we call each side's function
directly and compare the two RDF/XML files it wrote, by isomorphism.
"""
import json
import os
import sys
import tempfile
from pathlib import Path

from rdflib import Graph

from rdfeval import harness

_TMP = tempfile.mkdtemp(prefix="csv_owl_subclass_")

_PREFIX_CSV = """prefix,namespace
ex,http://example.org/onto#
"""

_SUBCLASS_CSV = """Subclass,Superclass,Restriction (onProperty),Restriction (quantifier)
ex:Cat,ex:Animal,,
ex:hasOwner some ex:Person,ex:Dog,,
ex:Cat & ex:Pet,ex:HouseholdAnimal,,
ex:Fish,ex:Animal,ex:livesIn,some
,ex:Water,ex:contains,all
,,,
"""

_prefix_path = os.path.join(_TMP, "prefixes.csv")
_subclass_path = os.path.join(_TMP, "subclass.csv")
with open(_prefix_path, "w", encoding="utf-8") as f:
    f.write(_PREFIX_CSV)
with open(_subclass_path, "w", encoding="utf-8") as f:
    f.write(_SUBCLASS_CSV)

_out_o = os.path.join(_TMP, "out_original.owl")
_out_t = os.path.join(_TMP, "out_translated.owl")

ex_dir = Path(__file__).resolve().parent
verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:csv_to_owl_subclass (output files, isomorphism)",
                 "diffs": [], "error": None}
try:
    ns_o, out_o = harness._exec_python(ex_dir / "original.py")
    ns_t, out_t = harness._exec_ldpy(ex_dir / "translated.ldpy")
    ns_o["csv_to_owl_subclass"](_subclass_path, _prefix_path, output_file=_out_o)
    ns_t["csv_to_owl_subclass"](_subclass_path, _prefix_path, output_file=_out_t)
    g_o = Graph().parse(_out_o, format="xml")
    g_t = Graph().parse(_out_t, format="xml")
    diffs = []
    if not harness.graphs_isomorphic(g_o, g_t):
        diffs.append(f"output graphs not isomorphic ({len(g_o)} vs {len(g_t)} triples)")
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)

print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict
