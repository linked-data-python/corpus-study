# Extracted from w3c-cg/sstim@39360a81b8 : scripts/preset-contract.py
# region: shacl_bounds (lines 180-236, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, BNode, RDF
SH = Namespace("http://www.w3.org/ns/shacl#")
SSTIM = Namespace("https://w3id.org/sstim#")
SSTIM_SH = Namespace("https://w3id.org/sstim/shapes#")
SH = Namespace("http://www.w3.org/ns/shacl#")
PARAMETER_MAP = {
    "carrierLeftHz": ("carrierFreqLeft", "fl"),
    "carrierRightHz": ("carrierFreqRight", "fr"),
    "centerHz": ("martigliCenterFreq", "mf0"),
    "amplitudeHz": ("martigliAmplitude", "ma"),
    "initialPeriodSeconds": ("martigliPeriodInitial", "mp0"),
    "finalPeriodSeconds": ("martigliPeriodFinal", "mp1"),
    "transitionSeconds": ("martigliTransitionDuration", "md"),
    "baseHz": ("baseFrequency", "f0"),
    "noteCount": ("noteCount", "nnotes"),
    "octaveSpan": ("octaveSpan", "noctaves"),
    "cycleSeconds": ("cycleDuration", "d"),
    # The catalog states the volume bound in prose rather than in a range
    # column, and states it twice inconsistently: the per-type tables said
    # "0-1" while the global limits section says 1.0 is invalid. The prose
    # is now corrected there, but there is still no range cell to read, so
    # only the SHACL half of this one is compared.
    "level": ("initialVolume", None),
}

def shacl_bounds(graph: Graph) -> tuple[dict[str, dict], list[str]]:
    """Bounds each SSTIM property carries across the four voice shapes.

    Two things are deliberately out of scope. The Patch Studio Track shapes
    reuse several of these properties under a different model (CLAUDE.md §4:
    the catalog preset and the live authoring patch are not the same object),
    and their bounds are theirs. Conditional constraints nested in sh:or — the
    breathing-reference rule that lifts the initial period to 3 s — hold under a
    condition rather than always, so reading them as bounds would report a
    contradiction that is not one.
    """
    voice_shapes = [
        SSTIM_SH.BinauralVoiceShape,
        SSTIM_SH.MartigliVoiceShape,
        SSTIM_SH.MartigliBinauralVoiceShape,
        SSTIM_SH.SymmetryVoiceShape,
    ]
    # permutationFunction is not in PARAMETER_MAP — it is a named enum in JSON
    # and an ordinal in RDF — but its ceiling is compared against the number
    # of names, so it must still be collected.
    wanted = {prop for prop, _ in PARAMETER_MAP.values()} | {"permutationFunction"}
    collected: dict[str, list[dict]] = {}
    for node_shape in voice_shapes:
        if (node_shape, None, None) not in graph:
            raise SystemExit(
                f"preset-contract: {node_shape} is missing — the voice shape "
                f"inventory here is stale and the comparison would silently "
                f"check less than it claims"
            )
        for shape in graph.objects(node_shape, SH.property):
            if not isinstance(shape, BNode):
                continue
            for path in graph.objects(shape, SH.path):
                local = str(path)[len(str(SSTIM)):] if str(path).startswith(str(SSTIM)) else None
                if local not in wanted:
                    continue
                entry = {
                    "min": number(graph.value(shape, SH.minInclusive)),
                    "minExclusive": number(graph.value(shape, SH.minExclusive)),
                    "max": number(graph.value(shape, SH.maxInclusive)),
                    "maxExclusive": number(graph.value(shape, SH.maxExclusive)),
                }
                if any(v is not None for v in entry.values()):
                    collected.setdefault(local, []).append(entry)

    problems: list[str] = []
    bounds: dict[str, dict] = {}
    for local, entries in collected.items():
        first = entries[0]
        if any(entry != first for entry in entries[1:]):
            problems.append(
                f"sstim:{local}: constrained differently in different voice shapes "
                f"({entries}) — the same parameter must mean the same thing in "
                f"every subtype that carries it"
            )
        bounds[local] = first
    return bounds, problems
