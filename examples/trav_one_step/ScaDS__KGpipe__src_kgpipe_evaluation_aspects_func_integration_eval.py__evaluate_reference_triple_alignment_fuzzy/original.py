# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe/evaluation/aspects/func/integration_eval.py
# region: evaluate_reference_triple_alignment_fuzzy (lines 325-384, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import RDFS, URIRef, Graph, RDF
from kgpipe.util.embeddings.st_emb import get_model

def evaluate_reference_triple_alignment_fuzzy(test_graph: Graph, ref_graph: Graph) -> BinaryClassificationResult:

    test_sp = test_graph.subject_predicates()

    model = get_model()

    def resolve_uris_as_labels(objs):
        for obj in objs:
            if isinstance(obj, URIRef):
                values = list(ref_graph.objects(obj, RDFS.label))
                for value in values:
                    yield str(value)
            else:
                yield str(obj)

    def check_obj_alignment(test_objs, reference_objs):
        test_values = list(set(resolve_uris_as_labels(test_objs)))
        reference_values = list(set(resolve_uris_as_labels(reference_objs)))
        return fuzzy_match(test_values, reference_values, model)

    # tp aligned triples (covered by reference  )
    # fp unknown triples (not covered by reference)
    # tn 
    # fn missing triples (covered by reference)

    tp = 0
    fp = 0
    tn = 0
    fn = 0

    checked_sp = set()

    for s, p in test_sp:
        ref_objs = list(ref_graph.objects(s, p))

        if len(ref_objs) > 0 and not (s, p) in checked_sp:
            checked_sp.add((s, p))
            test_objs = list(test_graph.objects(s, p))

            for idx, is_match in enumerate(check_obj_alignment(test_objs, ref_objs)):
                if is_match:
                    # print(f"tp: {s} {p} {test_objs[idx]}")
                    tp += 1
                else:
                    # print(f"fp: {s} {p} {test_objs[idx]}")
                    fp += 1

        else:
            #print(f"fp: {s} {p}")
            fp += 1

    # calculate fn
    reference_sp = ref_graph.subject_predicates()
    for s, p in reference_sp:
        test_objs = list(test_graph.objects(s, p))
        if len(test_objs) == 0:
            #print(f"fn: {s} {p}")
            fn += 1

    return BinaryClassificationResult(tp=tp, fp=fp, tn=tn, fn=fn)
