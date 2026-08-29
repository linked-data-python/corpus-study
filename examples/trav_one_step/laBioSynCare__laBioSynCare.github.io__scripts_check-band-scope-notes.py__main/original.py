# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/check-band-scope-notes.py
# region: main (lines 76-174, stratum trav_one_step)
# licence of the source repository: see meta.json
import sys
from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import SKOS
SSTIM = Namespace("https://w3id.org/sstim#")
SSTIM_V = Namespace("https://w3id.org/sstim/vocab#")
SSTIM_EX = Namespace("https://w3id.org/sstim/exposure#")
OUTCOME_WORDS = re.compile(
    r"\b("
    r"sleep|sleepiness|drowsy|drowsiness|insomnia|"
    r"relax\w*|calm\w*|stress|anxiet\w*|mood|depress\w*|"
    r"pain|analges\w*|"
    r"attention|focus\w*|concentrat\w*|alert\w*|vigilan\w*|"
    r"cognit\w*|memory|creativ\w*|meditat\w*|"
    r"heal\w*|therap\w*|treat\w*|symptom\w*|"
    r"down-regulation|up-regulation"
    r")\b",
    re.IGNORECASE,
)
MOVED_ASSOCIATIONS = {
    "deltaOscillation": 1,
    "thetaOscillation": 4,
    "alphaOscillation": 2,
    "smrOscillation": 1,
    "betaOscillation": 1,
    "gammaOscillation": 1,
}

def main() -> int:
    failures: list[str] = []

    graph = Graph()
    for path in module_paths():
        graph.parse(path, format="turtle")

    # ── 1. No band asserts an outcome ────────────────────────────────────────
    bands = [b for b in graph.subjects(RDF.type, SSTIM.FrequencyBand) if isinstance(b, URIRef)]
    if not bands:
        failures.append("no sstim:FrequencyBand concepts found — the lint would pass vacuously")

    checked = 0
    for band in bands:
        for predicate in (SKOS.scopeNote, SKOS.definition, SKOS.prefLabel, SKOS.altLabel):
            for value in graph.objects(band, predicate):
                checked += 1
                hit = OUTCOME_WORDS.search(str(value))
                if hit:
                    failures.append(
                        f"{band.split('#')[-1]}: {predicate.split('#')[-1]} claims an outcome "
                        f"({hit.group(0)!r}) — a frequency band is a Hz interval. "
                        f"Move it to the oscillation as an evidence claim or a knowledge-status "
                        f"assertion (ADR 0049)."
                    )

    # ── 2. No moved association was silently dropped ─────────────────────────
    for path in instance_paths():
        graph.parse(path, format="turtle")

    for name, expected in MOVED_ASSOCIATIONS.items():
        oscillation = SSTIM_V[name]
        assessed = set(graph.subjects(SSTIM.evaluatesSubject, oscillation))
        statuses = set(graph.objects(oscillation, SSTIM_EX.hasKnowledgeStatusAssertion))
        found = len(assessed) + len(statuses)
        if found < expected:
            failures.append(
                f"{name}: {found} recorded association(s), expected at least {expected}. "
                f"ADR 0049 moved these off the band scope notes; deleting one loses the "
                f"knowledge that it was claimed."
            )

    # ── 3. Frequency arithmetic holds ────────────────────────────────────────
    # ADR 0049 gave each oscillation a conventional ambit and the wider range it
    # actually occupies. Nothing checked that the second contains the first, or
    # that any band's interval runs the right way — both are the kind of error a
    # single mistyped digit makes and no reader notices.
    oscillations = 0
    for oscillation in sorted(graph.subjects(RDF.type, SSTIM.NeuralOscillationType), key=str):
        name = str(oscillation).split("#")[-1]
        band = next(graph.objects(oscillation, SSTIM.hasTypicalFrequencyBand), None)
        low = next(graph.objects(oscillation, SSTIM.extendedHzMin), None)
        high = next(graph.objects(oscillation, SSTIM.extendedHzMax), None)
        if band is None or low is None or high is None:
            failures.append(f"{name}: missing a typical band or an extended range")
            continue
        oscillations += 1
        if float(low) >= float(high):
            failures.append(f"{name}: extendedHzMin {low} is not below extendedHzMax {high}")
        band_low = next(graph.objects(band, SSTIM.hzMin), None)
        band_high = next(graph.objects(band, SSTIM.hzMax), None)
        if band_low is None or band_high is None:
            failures.append(f"{name}: typical band {str(band).split('#')[-1]} states no Hz interval")
        elif float(low) > float(band_low) or float(high) < float(band_high):
            failures.append(
                f"{name}: extended range {low}-{high} Hz does not contain its typical "
                f"band {band_low}-{band_high} Hz — an oscillation occupies at least "
                f"the ambit it is delimited by"
            )

    bands_with_interval = 0
    for band in bands:
        low = next(graph.objects(band, SSTIM.hzMin), None)
        high = next(graph.objects(band, SSTIM.hzMax), None)
        if low is None or high is None:
            failures.append(f"{str(band).split('#')[-1]}: states no hzMin/hzMax interval")
        else:
            bands_with_interval += 1
            # Single-frequency targets (alpha-10, gamma-40) are a point, so equal
            # bounds are correct; inverted bounds never are.
            if float(low) > float(high):
                failures.append(
                    f"{str(band).split('#')[-1]}: hzMin {low} exceeds hzMax {high}"
                )

    if failures:
        print(f"band-scope-notes: FAILED ({len(failures)})", file=sys.stderr)
        for failure in failures:
            print(f"  - {failure}", file=sys.stderr)
        return 1

    total = sum(MOVED_ASSOCIATIONS.values())
    print(
        f"band-scope-notes: passed ({len(bands)} bands, {checked} labels and notes free of "
        f"outcome claims; {total} moved associations still recorded; "
        f"{oscillations} oscillation ranges contain their ambits and "
        f"{bands_with_interval} band intervals run the right way)"
    )
    return 0
