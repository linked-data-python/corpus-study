# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/semtech_supplementary_gates_v6_6_0.py
# region: <module> (lines 114-121, stratum trav_single_value)
# licence of the source repository: see meta.json
# Context restored (see meta.json): HERE is the script's data directory
# (/home/claude/semtech-landscape in the real script) -- here this region's own
# directory, holding small stand-ins for the TTL files and the two tooling
# modules the script loads; `load`, `nodes`, `secnum` and `cls_iri` come from
# the context shim semtech_gates_ctx.py.
from pathlib import Path
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD
from semtech_gates_ctx import load, nodes, secnum, cls_iri
HERE = Path(__file__).resolve().parent
SEM = Namespace("http://example.org/semtech#")
T = load("taxonomy", "v1_0_0"); EC = load("enrichment_c", "v2_0_0")
tb = Graph().parse(f"{HERE}/02-ontology/semtech_tbox_v6_6_0.ttl")
ab = Graph().parse(f"{HERE}/02-ontology/semtech_abox_v6_6_0.ttl")
sh = Graph().parse(f"{HERE}/02-ontology/semtech_shacl_v6_6_0.ttl")
rs = Graph().parse(f"{HERE}/01-research/semtech_research_v6_6_0.ttl")
dc = Graph().parse(f"{HERE}/03-document/semtech_document_v6_6_0.ttl")
pg = Graph().parse(f"{HERE}/04-page/semtech_page_abox_v6_6_0.ttl")
IRI = {n["id"]: cls_iri(n) for n in nodes}
bad = []
bad = [n["id"] for n in nodes
       if str(tb.value(IRI[n["id"]], SEM.classCode) or "") != n["id"]
       or str(tb.value(IRI[n["id"]], SEM.sectionNumber) or "") != secnum[n["id"]]]
edges = [(s, p, o) for p in (SEM[k] for k in EC.REL_PROPS)
         for s, o in tb.subject_objects(p)]
sem_classes = set(IRI.values())
bad = [f"{s}|{o}" for s, p, o in edges if s not in sem_classes or o not in sem_classes]
bad = []
bad = []
need = [RDFS.label, DCTERMS.license, DCTERMS.rights, DCTERMS.rightsHolder, DCTERMS.publisher,
        DCTERMS.creator, DCTERMS.created, DCTERMS.modified, DCTERMS.identifier, OWL.versionInfo]
bad = []

for name, g in [("research", rs), ("tbox", tb), ("abox", ab), ("shacl", sh), ("document", dc), ("page", pg)]:
    onts = list(g.subjects(RDF.type, OWL.Ontology))
    if len(onts) != 1: bad.append(f"{name}:onts={len(onts)}"); continue
    o = onts[0]
    miss = [p.split("#")[-1].split("/")[-1] for p in need if not g.value(o, p)]
    if miss: bad.append(f"{name}:{miss}")
    if str(g.value(o, OWL.versionInfo)) != "6.6.0": bad.append(f"{name}:ver")
    if not str(g.value(o, OWL.versionIRI) or "").endswith("/6.6.0"): bad.append(f"{name}:viri")
