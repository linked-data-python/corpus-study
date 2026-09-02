# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v6_3_0.py
# region: <module> (lines 162-163, stratum add_in_loop)
# licence of the source repository: see meta.json
# Executability: BASEDIR, load(), nodes and cls_iri -- defined earlier in
# the same source file, just outside this region -- restored via
# context_predecl.py (context shim, see meta.json).
from rdflib import Graph, Namespace
from context_predecl import BASEDIR, load, nodes, cls_iri
en = load("enrichment_n", "v6_0_0")
SEM = Namespace("http://example.org/semtech#")
IRI = {n["id"]: cls_iri(n) for n in nodes}
g2 = Graph().parse(f"{BASEDIR}/02-ontology/semtech_tbox_v6_2_0.ttl")

for s_, p_, d_ in en.NEW_RELATIONS:
    g2.add((IRI[s_], SEM[p_], IRI[d_]))
