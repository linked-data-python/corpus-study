# Context shim (see meta.json): stand-in for the project's `config.Config`,
# of which only the class attribute `g` -- the single shared graph the real
# Flask app builds once at startup and every renderer reads from -- is used
# by this region. `g` is parsed from fixture.ttl once at import time; both
# original.py and translated.ldpy `from config import Config` the same
# module within one driver run (see driver.py), so they read the identical
# graph. The region only ever READS Config.g, so sharing one instance
# between the two sides changes nothing it can observe.
from pathlib import Path
from rdflib import Graph


class Config:
    g = Graph()
    g.parse(str(Path(__file__).resolve().parent / "fixture.ttl"), format="turtle")
