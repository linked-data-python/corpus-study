"""Validation driver for city-knowledge-graphs__python-2024__lab2_createTriples.py__createTriples.

createTriples() builds a local graph, prints it as Turtle, and serialises it to
./data/lab2_example_rdflib.ttl. Everything the region shows is therefore
output, and the harness compares all of it:

  * stdout: the "Saving graph" line and the Turtle text, which carries the
    prefix table (foaf, city, dbpo) and every triple in rdflib's canonical
    layout -- the blank node, subject of the reified statement and never an
    object, is written inline as `[]`, so its random id does not leak;
  * the file written under data/, compared as an RDF document (its graph);
  * the return value (None).

The directory data/ is created here: the region assumes the repository's own
lab2/data/ folder. Without it the region ends in FileNotFoundError after the
print, on both sides. original.py differs from the extracted region on one
character run: `.decode("utf-8")` after `g.serialize(...)` is dropped on both
sides (rdflib >= 6 returns str, so the call raised AttributeError and the
graph was never shown); this affects no RDF meaning.
"""
import os
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.chdir(HERE)
os.makedirs(HERE / "data", exist_ok=True)

from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='createTriples',
    calls=[((), {})],
)
