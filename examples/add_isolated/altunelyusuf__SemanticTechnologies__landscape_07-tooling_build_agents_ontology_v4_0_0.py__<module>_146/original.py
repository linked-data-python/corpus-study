# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/07-tooling/build_agents_ontology_v4_0_0.py
# region: <module> (lines 146-151, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, Literal, BNode
EC = load("enrichment_c", "v2_0_0"); EH = load("enrichment_h", "v4_0_0")
B = Namespace("http://example.org/backlog#")
gb = Graph(); gb.bind("backlog", B); gb.bind("ab", Namespace("http://example.org/semtech-agents-backlog#"))
AB = Namespace("http://example.org/semtech-agents-backlog#")
init = AB.AgentsInitiative

for eid, lbl, dfn in EH.BL_EPICS:
    e = AB[eid]
    bind_(e, [B.Epic], lbl, dfn, f"AG-{eid}", [(B.hasState, B.InProgress if eid in ("EP1", "EP2") else B.Proposed), (B.memberOfContainer, AB.AgentsBacklog)]
             + ([] if eid in ("EP1", "EP2") else [(B.notYetScoreable, Literal(True)),
                (B.hasScoreabilityReason, Literal("Open epic: its features carry no executable evidence yet; scoring before delivery would fabricate numbers.", lang="en"))]))
    gb.add((init, B.decomposesInto, e))
