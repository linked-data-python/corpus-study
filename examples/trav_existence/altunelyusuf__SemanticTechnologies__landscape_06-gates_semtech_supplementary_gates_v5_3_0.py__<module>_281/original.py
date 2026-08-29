# Extracted from altunelyusuf/SemanticTechnologies@bad0fa7c46 : landscape/06-gates/semtech_supplementary_gates_v5_3_0.py
# region: <module> (lines 281-281, stratum trav_existence)
# licence of the source repository: see meta.json
B2 = Namespace("http://example.org/backlog#")
gbk = Graph().parse(f"{HERE}/08-agents/agents_backlog_abox_v4_1_0.ttl")
done = [f for f in feats if (f, B2.hasState, B2.Done) in gbk]

ev_ok = all(gbk.value(f, B2.hasEvidence) is not None for f in done)
