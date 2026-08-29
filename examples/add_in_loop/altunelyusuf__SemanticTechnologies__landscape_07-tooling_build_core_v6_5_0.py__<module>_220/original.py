# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_core_v6_5_0.py
# region: <module> (lines 220-222, stratum add_in_loop)
# licence of the source repository: see meta.json
el = load("enrichment_l", "v5_3_0")
SEM = Namespace("http://example.org/semtech#")
g3 = Graph().parse(f"{BASEDIR}/02-ontology/semtech_abox_v6_4_0.ttl"); bump(g3)

for role_id, acts in el.PERFORMS.items():
    for act_id in acts:
        g3.add((SEM[role_id], SEM.performsActivity, SEM[act_id]))
