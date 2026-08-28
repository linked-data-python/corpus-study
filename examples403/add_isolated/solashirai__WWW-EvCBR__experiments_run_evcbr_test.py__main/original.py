# Extracted from solashirai/WWW-EvCBR@ac42338015 : experiments/run_evcbr_test.py
# region: main (lines 242-245, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef

with open((testdata_dir / "train.txt").resolve(), "r") as f:
    for line in f:
        t = line.strip().split("\t")
        main_kg.add((URIRef(t[0]), URIRef(t[1]), URIRef(t[2])))
