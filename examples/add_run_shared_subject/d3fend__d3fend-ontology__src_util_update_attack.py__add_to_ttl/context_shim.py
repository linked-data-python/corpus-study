# Context shim (see meta.json): the module-level names that
# add_to_ttl (d3fend/d3fend-ontology@cce593d61c, src/util/update_attack.py)
# takes from the rest of its file and from `build`, so the function
# executes outside the repository. Identical bindings for both
# representations.
#
#  * the tactic-class tables, get_framework_labels, get_framework_tactic_uris,
#    get_deprecated_comment and ensure_superclasses are copied VERBATIM from
#    update_attack.py (the `d3fend` namespace they use is redefined below,
#    identically).
#  * `build` (src/util/build.py) is not importable here: the package named
#    `build` of this environment is PyPA's. `get_graph` is a stub nothing
#    calls; `_xmlns` is the d3fend ontology namespace (the one the file's
#    own `d3fend` Namespace uses): `build.py` at this commit defines no
#    `_xmlns`, so the repository's own import does not resolve.
from rdflib import RDFS, Namespace, URIRef

d3fend = Namespace("http://d3fend.mitre.org/ontologies/d3fend.owl#")

_xmlns = "http://d3fend.mitre.org/ontologies/d3fend.owl#"


def get_graph(filename=None):
    raise NotImplementedError("stub: the region never calls it")


ENTERPRISE_TACTIC_CLASSES = {
    "CollectionTechnique",
    "CommandAndControlTechnique",
    "CredentialAccessTechnique",
    "DefenseEvasionTechnique",
    "DefenseImpairmentTechnique",
    "DiscoveryTechnique",
    "ExecutionTechnique",
    "ExfiltrationTechnique",
    "ImpactTechnique",
    "InitialAccessTechnique",
    "LateralMovementTechnique",
    "PersistenceTechnique",
    "PrivilegeEscalationTechnique",
    "ReconnaissanceTechnique",
    "ResourceDevelopmentTechnique",
    "StealthTechnique",
}

ICS_TACTIC_CLASSES = {
    "ATTACKICSCollectionTechnique",
    "ATTACKICSCommandAndControlTechnique",
    "ATTACKICSDiscoveryTechnique",
    "ATTACKICSEvasionTechnique",
    "ATTACKICSExecutionTechnique",
    "ATTACKICSImpactTechnique",
    "ATTACKICSImpairProcessControlTechnique",
    "ATTACKICSInhibitResponseFunctionTechnique",
    "ATTACKICSInitialAccessTechnique",
    "ATTACKICSLateralMovementTechnique",
    "ATTACKICSPersistenceTechnique",
    "ATTACKICSPrivilegeEscalationTechnique",
}

MOBILE_TACTIC_CLASSES = {
    "ATTACKMobileCollectionTechnique",
    "ATTACKMobileCommandAndControlTechnique",
    "ATTACKMobileCredentialAccessTechnique",
    "ATTACKMobileDefenseEvasionTechnique",
    "ATTACKMobileDiscoveryTechnique",
    "ATTACKMobileExecutionTechnique",
    "ATTACKMobileExfiltrationTechnique",
    "ATTACKMobileImpactTechnique",
    "ATTACKMobileInitialAccessTechnique",
    "ATTACKMobileLateralMovementTechnique",
    "ATTACKMobilePersistenceTechnique",
    "ATTACKMobilePrivilegeEscalationTechnique",
}

TACTIC_CLASSES_BY_FRAMEWORK = {
    "enterprise": ENTERPRISE_TACTIC_CLASSES,
    "ics": ICS_TACTIC_CLASSES,
    "mobile": MOBILE_TACTIC_CLASSES,
}


def get_framework_labels(original_label, framework):
    """
    Given a technique's original label (original_label) and a framework,
    return a tuple (new_label, pref_label) where:
      • new_label is the label to store as rdfs:label. For "ics" and "mobile"
        a suffix is appended (e.g., " - ATTACK ICS" or " - ATTACK Mobile").
      • pref_label is the preferred label (to be stored as skos:prefLabel) or
        None if no separate preferred label is needed.
    For enterprise, no changes are made.
    """
    fw = framework.lower()
    if fw == "enterprise":
        return original_label, None
    elif fw == "ics":
        return original_label + " - ATTACK ICS", original_label
    elif fw == "mobile":
        return original_label + " - ATTACK Mobile", original_label
    else:
        return original_label, None


def get_framework_tactic_uris(framework):
    return {d3fend[class_name] for class_name in TACTIC_CLASSES_BY_FRAMEWORK[framework]}


def get_deprecated_comment(tech_entry, _framework):
    revoked_by = tech_entry.get("revoked_by")
    if revoked_by:
        return f"This technique has been revoked by {revoked_by}"

    description = tech_entry["data"].get("description", "")
    first_line = description.strip().split("\n")[0].strip()
    if first_line and "deprecated" in first_line.lower():
        return first_line

    return "This technique has been deprecated."


def ensure_superclasses(graph, attack_uri, subclass, framework, subtechnique):
    desired = set()

    if subtechnique:
        target = d3fend[subclass]
        desired.add(target)
    else:
        for subclass_of in subclass:
            desired.add(d3fend[subclass_of])

    for target in desired:
        if (attack_uri, RDFS.subClassOf, target) not in graph:
            graph.add((attack_uri, RDFS.subClassOf, target))

    tactic_uris = get_framework_tactic_uris(framework)
    for obj in list(graph.objects(attack_uri, RDFS.subClassOf)):
        if isinstance(obj, URIRef) and obj in tactic_uris and obj not in desired:
            graph.remove((attack_uri, RDFS.subClassOf, obj))
