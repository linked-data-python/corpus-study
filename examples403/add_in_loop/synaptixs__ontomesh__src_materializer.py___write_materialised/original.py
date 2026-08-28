# Extracted from synaptixs/ontomesh@f771c8c4ee : src/materializer.py
# region: _write_materialised (lines 574-603, stratum add_in_loop)
# licence of the source repository: see meta.json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from rdflib import BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.namespace import OWL, PROV, RDF, RDFS, XSD
TOOLKIT_NS = Namespace("https://ontology.example.com/toolkit/materializer/")

def _write_materialised(ontology_path: str, extras: Sequence[str],
                        engine_results: Sequence[EngineResult],
                        out_path: str) -> int:
    g = Graph()
    _bind_prefixes(g)
    g.parse(ontology_path, format="turtle")
    for extra in extras:
        if extra and os.path.isfile(extra):
            try:
                g.parse(extra, format="turtle")
            except Exception:  # noqa: BLE001 — never let this kill the run
                pass
    for er in engine_results:
        if er.output_path and os.path.isfile(er.output_path):
            try:
                g.parse(er.output_path, format="turtle")
            except Exception:  # noqa: BLE001
                pass

    # Top-level provenance summary block: one prov:Activity per engine.
    materialisation = TOOLKIT_NS["materialisation/" + _stamp()]
    g.add((materialisation, RDF.type, PROV.Activity))
    g.add((materialisation, RDFS.label, Literal("Phase B materialisation run")))
    g.add((materialisation, PROV.endedAtTime,
           Literal(datetime.now(timezone.utc).isoformat(), datatype=XSD.dateTime)))
    for er in engine_results:
        g.add((materialisation, PROV.wasInformedBy, er.activity_iri))

    g.serialize(destination=out_path, format="turtle")
    return len(g)
