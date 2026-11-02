"""Validation driver for altunelyusuf__SemanticTechnologies__landscape_07-tooling_build_core_v5_3_0.py__<module>_118.

Module-level region (no function to call): entry=None executes both
original.py and translated.ldpy and compares every rdflib Graph found in the
module globals (g2, by isomorphism and prefix bindings) plus the other
module-level values both sides define (BASEDIR, the loop's last
ap/lab/dfn/p).

`BASEDIR` and `S` are restored by context_shim.py (see meta.json); `BASEDIR`
points at 02-ontology/semtech_tbox_v5_2_0.ttl, a stand-in that already holds
a class, a property the region does not touch, and one of the three the
region declares (sem:criticalTip, with a French label): the region's
additions are checked against existing data, not an empty graph. The
language tag of each of the three literals per property is part of the
isomorphism (rdfs:label, skos:definition and dcterms:source all `@en`).
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
