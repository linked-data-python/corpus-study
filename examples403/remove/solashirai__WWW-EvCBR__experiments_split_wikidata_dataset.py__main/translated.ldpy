# Extracted from solashirai/WWW-EvCBR@ac42338015 : experiments/split_wikidata_dataset.py
# region: main (lines 143-159, stratum remove)
# licence of the source repository: see meta.json
while remove_nodes:
    for rn in remove_nodes:
        kg.remove((None, None, rn))
        kg.remove((rn, None, None))
    remove_nodes = []
    for n in kg.all_nodes():
        conn_count = 0
        for s, p, in kg.subject_predicates(object=n):
            conn_count += 1
            if conn_count > 1:
                break
        for p, o in kg.predicate_objects(subject=n):
            conn_count += 1
            if conn_count > 1:
                break
        if conn_count <= 1:
            remove_nodes.append(n)
