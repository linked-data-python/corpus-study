# Extracted from TDCC-NES/askwol@3534557e8b : src/askwol/term_inventory.py
# region: check_domains_ranges (lines 219-311, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL, RDF, RDFS, XSD
from askwol.deprecation import deprecation_marker
from askwol.iri_utils import is_external as _is_external, local_name as _local_name, ontology_namespaces as _ontology_namespaces
from askwol.models import (
    DatatypeReport,
    DatatypeUsage,
    DomainRangeCheck,
    DomainRangeReport,
    InternalTermEntry,
    Status,
    TermInventoryReport,
)
from askwol.shacl_runner import run_shapes
_SHAPES_FILE = "term_inventory.ttl"
OBJECT_PROPERTY = "Object property"
DATATYPE_PROPERTY = "Datatype property"

def check_domains_ranges(graph: Graph) -> DomainRangeReport:
    """Check that object and datatype properties have sound domains and ranges.

    Only direct ``rdfs:domain`` / ``rdfs:range`` triples are considered;
    domains and ranges inherited via super-properties or inference are not
    followed, consistent with the rest of askwol.
    """
    if not _ontology_namespaces(graph):
        return DomainRangeReport(status=Status.SKIP, message="no owl:Ontology declaration found")

    classified = _classify_internal_terms(graph)
    properties = {
        uri: cat
        for uri, cat in classified.items()
        if cat in (OBJECT_PROPERTY, DATATYPE_PROPERTY)
    }
    if not properties:
        return DomainRangeReport(
            status=Status.SKIP,
            message="no object or datatype properties are defined in the ontology's own namespace",
        )

    violations: dict[str, dict[str, str]] = {}
    for result in run_shapes(graph, _SHAPES_FILE):
        if result.name in (
            "DomainMissing", "RangeMissing", "DomainIsDatatype",
            "ObjectPropertyRangeIsDatatype", "DatatypePropertyRangeIsClass",
        ):
            violations.setdefault(result.focus_node, {})[result.name] = result.message

    checks: list[DomainRangeCheck] = []
    object_count = 0
    datatype_count = 0

    for uri, category in sorted(properties.items()):
        subject = URIRef(uri)
        has_domain = any(True for _ in graph.objects(subject, RDFS.domain))
        has_range = any(True for _ in graph.objects(subject, RDFS.range))

        if category == OBJECT_PROPERTY:
            object_count += 1
        else:
            datatype_count += 1

        node_violations = violations.get(uri, {})
        marker = deprecation_marker(graph, subject)
        problems = [
            node_violations[name]
            for name in ("DomainIsDatatype", "ObjectPropertyRangeIsDatatype", "DatatypePropertyRangeIsClass")
            if name in node_violations
        ]
        missing = [node_violations[name] for name in ("DomainMissing", "RangeMissing") if name in node_violations]

        if marker:
            status = Status.OK
            message = "Deprecated; domain and range are not checked."
        elif problems:
            status = Status.FAIL
            message = " ".join(problems)
        elif missing:
            status = Status.WARN
            message = " ".join(missing)
        else:
            status = Status.OK
            message = "Domain and range declared."

        checks.append(
            DomainRangeCheck(
                term=uri,
                display_name=_local_name(uri),
                category=category,
                has_domain=has_domain,
                has_range=has_range,
                status=status,
                message=message,
                deprecated=marker,
            )
        )

    if any(c.status == Status.FAIL for c in checks):
        overall = Status.FAIL
    elif any(c.status == Status.WARN for c in checks):
        overall = Status.WARN
    else:
        overall = Status.OK

    return DomainRangeReport(
        total_properties=len(checks),
        object_properties=object_count,
        datatype_properties=datatype_count,
        checks=checks,
        status=overall,
    )
