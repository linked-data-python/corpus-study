# Extracted from w3c-cg/sstim@39360a81b8 : scripts/sstim-definition-coverage.py
# region: main (lines 132-173, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib.namespace import SKOS, RDFS, OWL
BREVITY_ALLOWED = {
    "eventPlaybackStart", "eventPlaybackEnd", "eventPause", "eventResume",
    "modelInVitro", "modelInVivo",
}
MIN_DEFINITION = 30
MIN_NOVEL_WORDS = 3
RESTATES_LABEL = {
    "approachEpidural", "approachIntrathecal", "mediumRigidSurfaceContact",
    "modelHuman", "modelInVitro", "phenomenonAutonomicNeuralRegulation",
    "phenomenonConnectivityOrPlasticity", "phenomenonExcitabilityOrFiring",
    "phenomenonNeurochemicalSignaling", "phenomenonSynapticTransmission",
    "resolutionUnchanged", "searchEligibilityCriteria", "severityUnknown",
    "targetCranialNerve", "targetPeripheralNerve", "targetSpinalCord",
    "visualDensity",
}

for kind, terms in subjects.items():
    for term in sorted(terms, key=str):
        name = local(term)
        definitions = [str(d).strip() for d in graph.objects(term, SKOS.definition)]
        if not definitions:
            failures.append(
                f"{kind} {name}: no skos:definition. A scope note is not a "
                f"definition, and pyLODE publishes this term blank."
            )
            continue
        checked += 1
        best = max(definitions, key=len)
        labels = [
            str(l)
            for predicate in (SKOS.prefLabel, RDFS.label)
            for l in graph.objects(term, predicate)
        ]
        if any(best.rstrip(".").casefold() == l.casefold() for l in labels):
            failures.append(f"{kind} {name}: the definition only restates the label")
        elif len(best) < MIN_DEFINITION and name not in BREVITY_ALLOWED:
            failures.append(
                f"{kind} {name}: definition is {len(best)} characters "
                f"({best!r}) — too short to distinguish it from a sibling. Add "
                f"it to BREVITY_ALLOWED if the brevity is deliberate."
            )
        else:
            novel = _content_words(best) - set().union(
                *(_content_words(l) for l in labels)
            ) if labels else _content_words(best)
            restates = len(novel) < MIN_NOVEL_WORDS
            if restates and name not in RESTATES_LABEL:
                failures.append(
                    f"{kind} {name}: the definition adds {len(novel)} content "
                    f"word(s) the label does not have ({best!r}) — say what "
                    f"distinguishes it from its siblings, or record it in "
                    f"RESTATES_LABEL deliberately."
                )
            elif not restates and name in RESTATES_LABEL:
                failures.append(
                    f"{kind} {name}: no longer restates its label — remove it "
                    f"from RESTATES_LABEL so the recorded debt stays honest."
                )
