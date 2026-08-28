# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/semtech_supplementary_gates_v4_1_0.py
# region: <module> (lines 83-87, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, OWL, SKOS, DCTERMS, XSD
SEM = Namespace("http://example.org/semtech#")
ab = Graph().parse(f"{HERE}/02-ontology/semtech_abox_v4_1_0.ttl")
bad = []
bad = [n["id"] for n in nodes
       if str(tb.value(IRI[n["id"]], SEM.classCode) or "") != n["id"]
       or str(tb.value(IRI[n["id"]], SEM.sectionNumber) or "") != secnum[n["id"]]]
bad = [f"{s}|{o}" for s, p, o in edges if s not in sem_classes or o not in sem_classes]
kind_cls = {SEM[f"Kind{k}"] for k in EC.KIND_DEFNS}
insts = set(ab.subjects(SEM.hasSourceProvenance, None))
bad = []
bad = []
bad = []
bad = [f for r, _, fs in os.walk(HERE) for f in fs
       if "__pycache__" not in r and not pat.match(f)]

for i in insts:
    ks = [t for t in ab.objects(i, RDF.type) if t in kind_cls]
    notes = list(ab.objects(i, SEM.instanceKindNote))
    if len(ks) != 1 or len(notes) != 1 or str(notes[0]) != str(ks[0]).split("#Kind")[-1]:
        bad.append(str(i).split("#")[-1])
