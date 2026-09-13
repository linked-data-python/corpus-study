# Context shim (see meta.json): subset of scripts/check-band-scope-notes.py
# from laBioSynCare/laBioSynCare.github.io@6dd8224b03. `main` locates its
# input graph through two helpers -- one reads a JSON manifest, the other
# walks a directory tree -- that are path discovery, not RDF reading, and
# are absent from the extracted region's context. Both representations
# import the same two functions, pointed at the same local fixture files.
from pathlib import Path

_HERE = Path(__file__).resolve().parent


def module_paths():
    return [_HERE / "fixture_module.ttl"]


def instance_paths():
    return [_HERE / "fixture_instance.ttl"]
