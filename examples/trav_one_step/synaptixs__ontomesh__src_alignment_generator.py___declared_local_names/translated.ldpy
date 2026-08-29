# Extracted from synaptixs/ontomesh@f771c8c4ee : src/alignment_generator.py
# region: _declared_local_names (lines 231-256, stratum trav_one_step)
# licence of the source repository: see meta.json
import os

def _declared_local_names(output_dir: str, filename: str) -> set[str]:
    """Local names of every subject declared in a generated Turtle file.

    Parsed with rdflib when available; falls back to a line scan so the
    alignment phase still runs in a minimal install.
    """
    path = os.path.join(output_dir, filename)
    if not os.path.isfile(path):
        return set()
    try:
        import rdflib
        g = rdflib.Graph()
        g.parse(path, format="turtle")
        return {str(s).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
                for s in g.subjects() if isinstance(s, rdflib.URIRef)}
    except Exception:
        names: set[str] = set()
        try:
            with open(path) as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith(":") and len(stripped) > 1:
                        names.add(stripped[1:].split()[0].rstrip(";,."))
        except OSError:
            return set()
        return names
