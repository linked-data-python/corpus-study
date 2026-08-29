# Extracted from laBioSynCare/laBioSynCare.github.io@6dd8224b03 : scripts/generate-hed-bundle.py
# region: read_sweep (lines 175-201, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef
S = lambda name: URIRef(SSTIM + name)  # noqa: E731

def read_sweep(graph: Graph) -> dict | None:
    """The one declarative modulation in SSTIM that a single row cannot express.

    A steady periodic modulation — a flicker rate, a beat frequency — is fully
    described by its rate, so one row carrying that rate is honest. A *parameter
    that itself changes across the session* is not: a Martigli breathing period
    gliding from mp0 to mp1 over md seconds has no single value to put in a
    column. That distinction, not "is anything oscillating", is what decision 5
    is about, so only the sweep is detected here.

    Returns None when the configuration is fixed.
    """
    for track in graph.subjects(S("martigliPeriodInitial"), None):
        mp0 = next(graph.objects(track, S("martigliPeriodInitial")), None)
        mp1 = next(graph.objects(track, S("martigliPeriodFinal")), None)
        md = next(graph.objects(track, S("martigliTransitionDuration")), None)
        if mp0 is None or mp1 is None or md is None:
            continue
        if float(mp0) == float(mp1):
            continue  # declared, but not actually sweeping
        return {
            "track": local(track),
            "mp0": float(mp0),
            "mp1": float(mp1),
            "md": float(md),
        }
    return None
