# Extracted from kumagallium/asterism@f0977d4d3a : scripts/build_demo_assets.py
# region: _merge_and_trim (lines 179-202, stratum remove)
# licence of the source repository: see meta.json
from pathlib import Path
from rdflib import Graph, URIRef
X_VALUES = URIRef(SD + "xValuesJSON")
Y_VALUES = URIRef(SD + "yValuesJSON")
SEED = _REPO / "datasets" / "starrydata" / "seed"
OUT = _REPO / "docs" / "demo" / "data"

def _merge_and_trim() -> tuple[Path, dict[str, int]]:
    g = Graph()
    for name in ("papers.ttl", "samples.ttl", "curves.ttl"):
        g.parse(SEED / name, format="turtle")

    OUT.mkdir(parents=True, exist_ok=True)
    full = OUT / "_full.ttl"
    g.serialize(destination=str(full), format="turtle")

    featured = set(_featured_iris(full))

    stripped = 0
    for subj in {s for s, _, _ in g.triples((None, X_VALUES, None))}:
        if str(subj) in featured:
            continue
        g.remove((subj, X_VALUES, None))
        g.remove((subj, Y_VALUES, None))
        stripped += 1

    merged = OUT / "starrydata-demo.ttl"
    g.serialize(destination=str(merged), format="turtle")
    full.unlink(missing_ok=True)

    return merged, {"stripped_curve_arrays": stripped, "featured": len(featured)}
