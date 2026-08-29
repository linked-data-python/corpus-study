# Extracted from tgbugs/pyontutils@cb3efcd10f : nifstd/nifstd_tools/aba_uberon.py
# region: main (lines 35-46, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib

for sub in abagraph.subjects(rdflib.RDF.type, rdflib.OWL.Class):
    if not sub.startswith(nses[ABA_PREFIX[:-1]]['']):
        continue
    subkey = ABA_PREFIX + sub.rsplit('/',1)[1]
    sub = rdflib.URIRef(sub)
    abalabs[subkey] = [o for o in abagraph.objects(rdflib.URIRef(sub), rdflib.RDFS.label)][0].toPython()
    syns = []
    for s in abagraph.objects(sub, syn_iri):
        syns.append(s.toPython())
    abasyns[subkey] = syns

    abaacro[subkey] = [a.toPython() for a in abagraph.objects(sub, acro_iri)]
