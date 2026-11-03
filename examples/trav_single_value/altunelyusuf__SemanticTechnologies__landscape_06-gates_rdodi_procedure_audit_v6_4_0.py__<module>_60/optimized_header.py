# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/rdodi_procedure_audit_v6_4_0.py
# region: <module> (lines 60-60, stratum trav_single_value)
# licence of the source repository: see meta.json
# Context restored (see meta.json): Graph/Namespace were imported earlier in
# the real script; HERE is the real script's own directory constant (used
# to locate sibling pipeline stage outputs) -- here it is this region's own
# directory, holding a small stand-in for the real
# landscape/01-research/semtech_research_v6_4_0.ttl.
from pathlib import Path
from rdflib import Graph, Namespace
from rdflib.namespace import SKOS
HERE = Path(__file__).resolve().parent
RES = Namespace("http://example.org/semtech/research#")
rs = Graph().parse(f"{HERE}/01-research/semtech_research_v6_4_0.ttl")

sc = str(rs.value(RES.ResearchCorpus, SKOS.note) or "")
