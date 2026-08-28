# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/semtech_supplementary_gates_v4_3_0.py
# region: <module> (lines 81-81, stratum trav_one_step)
# licence of the source repository: see meta.json
SEM = Namespace("http://example.org/semtech#")
ab = Graph().parse(f"{HERE}/02-ontology/semtech_abox_v4_3_0.ttl")

insts = set(ab.subjects(SEM.hasSourceProvenance, None))
