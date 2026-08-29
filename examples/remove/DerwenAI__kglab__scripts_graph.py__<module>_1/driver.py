"""Validation driver for DerwenAI__kglab__scripts_graph.py__<module>_1.

NOT RUNNABLE in the evaluation venv -- the pair is `excluded`, see meta.json.

The region is the demo script of kglab's own rdflib *store plugin*: it
registers `kglab.PropertyStore` and does all its work through a
`rdflib.Graph(store="kglab")`.  Executing it therefore needs kglab, and
`kglab/graph.py` needs numpy (the store keeps its node/relation names in numpy
arrays), chocolate (its `query`/`update` filter their kwargs with it),
cryptography (the BLAKE2b digest the store updates on every triple) and
icecream.  None of the four is installed, and standing in for them would mean
re-implementing the very object the region exercises -- so the region is left
translated but unproven rather than proven against a fake.

Two further obstacles, recorded for whoever installs the dependencies:
  * the whole region sits under `if __name__ == "__main__":`, and the harness
    executes both modules with `__name__` set to `__original__` /
    `__translated__`, so nothing would run without neutralising that guard
    identically on both sides;
  * the region's observable is `graph`, whose last triple is chosen by the
    store's iteration order -- deterministic for one store, but part of what
    the comparison would be measuring.

The three islands the translation uses were nevertheless checked, one by one,
against the region's own data on a plain `rdflib.Graph`; see meta.json.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry=None,
    calls=None,
)
