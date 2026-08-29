# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/public-claim-gate-negative.py
# region: messages_by_focus (lines 358-364, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF
SH = Namespace("http://www.w3.org/ns/shacl#")

def messages_by_focus(results: Graph) -> dict[str, list[str]]:
    reported: dict[str, list[str]] = {}
    for result in results.subjects(RDF.type, SH.ValidationResult):
        for focus in results.objects(result, SH.focusNode):
            for message in results.objects(result, SH.resultMessage):
                reported.setdefault(str(focus), []).append(str(message))
    return reported
