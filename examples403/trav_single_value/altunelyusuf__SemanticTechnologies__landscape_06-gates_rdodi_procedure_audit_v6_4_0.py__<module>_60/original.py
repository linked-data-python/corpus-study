# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/rdodi_procedure_audit_v6_4_0.py
# region: <module> (lines 60-60, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD
RES = Namespace("http://example.org/semtech/research#")
rs = Graph().parse(f"{HERE}/01-research/semtech_research_v6_4_0.ttl")

sc = str(rs.value(RES.ResearchCorpus, SKOS.note) or "")
