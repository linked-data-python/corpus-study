# Context shim (see meta.json): subset of Display-Lab/scaffold@d368cfe17c —
# src/utils/namespace (the vocabularies) and the two helpers of
# src/candidate_pudding/candidate_pudding.py that the region calls, so that the
# region executes outside the package.  Identical bindings for both
# representations.
#
# CPO, PSDO, IAO and RO are AliasingDefinedNamespace classes upstream: the
# readable attribute is an alias for an obo identifier (CPO.has_causal_pathway
# is obo:cpo_0000056, not obo:has_causal_pathway).  Only the terms the region
# and its two helpers use are reproduced, with the IRIs the aliases resolve to.
# SLOWMO declares no alias, so a plain Namespace gives the same terms.
from rdflib import BNode, Literal, Namespace, URIRef
from rdflib.namespace import RDF
from rdflib.resource import Resource

OBO = Namespace("http://purl.obolibrary.org/obo/")
SCHEMA = Namespace("http://schema.org/")
SLOWMO = Namespace("http://example.com/slowmo#")


class CPO:
    has_causal_pathway = OBO.cpo_0000056


class PSDO:
    motivating_information = OBO.PSDO_0000200
    comparator_content = OBO.PSDO_0000093


class IAO:
    is_about = OBO.IAO_0000136


class RO:
    has_disposition = OBO.RO_0000091


DEFAULT_DISPLAY = URIRef(
    "https://schema.metadatacenter.org/properties/5b4f16a9-feb7-4724-8741-2739d8808760"
)


def add_motivating_information(candidate: Resource):
    """From the same module, trimmed: the loop that filters the motivating
    information through src.bitstomach.signals.Signal is dropped (it needs the
    whole package).  What the region uses of it is unchanged: the selection of
    the motivating information regarding the candidate's measure, and the None
    that says there is none — which is what sends the region to its remove."""
    performance_content = candidate.graph.resource(BNode("performance_content"))
    measure = candidate.value(SLOWMO.RegardingMeasure)
    motivating_informations = [
        motivating_info
        for motivating_info in performance_content[PSDO.motivating_information]
        if motivating_info.value(SLOWMO.RegardingMeasure) == measure
    ]

    if not motivating_informations:
        return None

    for motivating_information in motivating_informations:
        candidate.add(PSDO.motivating_information, motivating_information)

    return candidate


def add_convenience_properties(candidate: Resource):
    """From the same module, verbatim."""
    candidate[SLOWMO.name] = candidate.value(
        SLOWMO.AncestorTemplate / URIRef("http://schema.org/name")
    )

    candidate[URIRef("psdo:PerformanceSummaryTextualEntity")] = candidate.value(
        SLOWMO.AncestorTemplate
        / URIRef(
            "https://schema.metadatacenter.org/properties/6b9dfdf9-9c8a-4d85-8684-a24bee4b85a8"
        )
    )

    comparator = next(
        (
            ttype
            for ttype in candidate[SLOWMO.AncestorTemplate / IAO.is_about]
            if ttype[RDF.type : PSDO.comparator_content]
        ),
        None,
    )

    candidate[SLOWMO.RegardingComparator] = comparator or Literal(None)
    candidate[SLOWMO.Display] = candidate.value(
        SLOWMO.AncestorTemplate / DEFAULT_DISPLAY
    )
    return candidate
