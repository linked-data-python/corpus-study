# Extracted from synaptixs/ontomesh@f771c8c4ee : scripts/ontology_gate.py
# region: collect (lines 221-268, stratum ns_def_local)
# licence of the source repository: see meta.json
from typing import Any, Dict, List, Optional, Tuple

def collect(output_dir: str) -> Dict[str, Any]:
    paths = _turtle_files(output_dir)
    graphs, failures = _parse_all(paths)
    authored = _authored_graph(graphs)

    owl_ns = rdflib.OWL
    restrictions = _count_predicate_objects(authored, rdflib.RDF.type, owl_ns.Restriction)
    multi_count, multi_worst = _multi_domain(authored)
    thing_ranges = _count_predicate_objects(authored, rdflib.RDFS.range, owl_ns.Thing)
    cq_returning, cq_failing, cq_total = _cq_rows(output_dir)

    # Phase 5 capabilities. Counted as instances, not declarations: a
    # vocabulary nothing uses is the failure mode this roadmap exists to
    # remove, so the metric tracks reified records rather than classes.
    prov_ns = rdflib.Namespace("http://www.w3.org/ns/prov#")
    ns = rdflib.Namespace("https://ontology.example.com/enterprise/")
    prov_chains = _count_predicate_objects(authored, rdflib.RDF.type, ns.DerivationActivity)
    temporal_extents = _count_predicate_objects(authored, rdflib.RDF.type, ns.TemporalExtent)
    quantity_values = _count_predicate_objects(authored, rdflib.RDF.type, ns.QuantityValue)
    participations = _count_predicate_objects(authored, rdflib.RDF.type, ns.Participation)

    # Phase 6: pitfalls firing, from the quality report.
    pitfalls_firing, pitfalls_critical = _pitfall_counts(output_dir)

    metrics = {
        "turtle_parse_failures":       len(failures),
        "multi_domain_properties":     multi_count,
        "worst_domain_count":          multi_worst,
        "alignment_subjects_unbound":  _alignment_unbound(graphs),
        "malformed_iris":              _malformed_iris(authored),
        "object_properties_ranged_at_thing": thing_ranges,
        "owl_restrictions":            restrictions,
        "cq_tests_returning_rows":     cq_returning,
        "cq_tests_failing":            cq_failing,
        "prov_chains":                 prov_chains,
        "temporal_extents":            temporal_extents,
        "quantity_values":             quantity_values,
        "participations":              participations,
        "pitfalls_firing":             pitfalls_firing,
        "pitfalls_critical":           pitfalls_critical,
    }
    detail = {
        "turtle_files_scanned": len(paths),
        "turtle_files_parsed":  len(graphs),
        "cq_tests_total":       cq_total,
        "parse_failures":       failures,
    }
    return {"metrics": metrics, "detail": detail}
