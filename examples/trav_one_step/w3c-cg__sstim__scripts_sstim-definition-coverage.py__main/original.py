# Extracted from w3c-cg/sstim@39360a81b8 : scripts/sstim-definition-coverage.py
# region: main (lines 132-173, stratum trav_one_step)
# licence of the source repository: see meta.json
#
# `subjects`, `graph`, `local`, `_content_words`, `failures`, `checked` are
# restored here (see meta.json) so the loop is executable outside `main`.
# `graph` is the project's own real ontology, loaded exactly as `main` loads
# it (same manifest, same modules) from the repository checkout at this
# commit -- not a synthetic stand-in, since the whole point of this region
# is checking real term definitions.
from pathlib import Path
import json
from rdflib import RDF, URIRef
from rdflib.namespace import SKOS, RDFS, OWL
from rdflib import Graph

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

import re
_STOPWORDS = frozenset(
    "the a an of in to for and or is are was were be been being with by on at as"
    " that which it its this these those from into over under between within not"
    " no any all each per such other than then when where while about".split()
)


def _content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.casefold())} - _STOPWORDS


BASE = "https://w3id.org/sstim"
_REPO = (
    Path(__file__).resolve().parents[3]
    / "corpus" / "repos" / "w3c-cg__sstim"
)
_ROOT = _REPO
_ONTOLOGY = _ROOT / "static" / "ontology"
_manifest = json.loads((_ONTOLOGY / "manifest.json").read_text(encoding="utf-8"))

graph = Graph()
for module in _manifest["modules"]:
    graph.parse(_ROOT / module["source"]["path"], format="turtle")


def ours(term) -> bool:
    return isinstance(term, URIRef) and str(term).startswith(BASE)


def local(term) -> str:
    text = str(term)
    return text.split("#")[-1] if "#" in text else text.rsplit("/", 1)[-1]


subjects = {
    "concept": {c for c in graph.subjects(RDF.type, SKOS.Concept) if ours(c)},
    "class": {c for c in graph.subjects(RDF.type, OWL.Class) if ours(c)},
    "property": {
        p
        for t in (OWL.ObjectProperty, OWL.DatatypeProperty)
        for p in graph.subjects(RDF.type, t)
        if ours(p)
    },
}

failures: list[str] = []
checked = 0

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
