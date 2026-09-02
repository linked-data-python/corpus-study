# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe_tasks/entity_resolution/fusion/preference.py
# region: select_first_value (lines 28-101, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import OWL, Graph, URIRef, RDFS, RDF, SKOS
from pathlib import Path
from typing import Dict, List, Optional
import json
import os
import tempfile
from context_shim import (DataFormat, Data, Registry, OntologyUtil,
                          TARGET_ONTOLOGY_NAMESPACE, TrackRecord)  # context shim -- see meta.json

@Registry.task(
    input_spec={"source": DataFormat.RDF_NTRIPLES, "target": DataFormat.RDF_NTRIPLES},
    output_spec={"output": DataFormat.RDF_NTRIPLES},
    description="Merge RDF entities using first value fusion",
    category=["EntityResolution", "Fusion"]
)
def select_first_value(inputs: Dict[str, Data], outputs: Dict[str, Data]):
    """
    For two KGs A and B, merge A into B where for each s_p and
    1) p is fusable and B does not have any s_p_o or
    2) p is not fusable erge all s_p_o
    """
    ontology_path = os.environ.get("ONTOLOGY_PATH", "false")
    if ontology_path == "false":
        raise ValueError("ONTOLOGY_PATH is not set")

    ontology = OntologyUtil.load_ontology_from_file(Path(ontology_path))
    allowed_predicates = set[str]([str(p.uri) for p in ontology.properties]+[str(RDFS.label), str(RDF.type), str(SKOS.altLabel)])
    fusable_properties = set[str]([str(p.uri) for p in ontology.properties if p.max_cardinality == 1]+[str(RDFS.label), str(RDF.type)])

    def is_fusable(p):
        return str(p) in fusable_properties

    source_graph = Graph()
    source_graph.parse(inputs["source"].path, format="nt")
    seed_graph = Graph() # seed graph
    seed_graph.parse(inputs["target"].path, format="nt")

    current_subjects = set[str]([str(s) for s in seed_graph.subjects(unique=True)])

    selected: List[TrackRecord] = []
    discarded: List[TrackRecord] = []

    for s, p, o in source_graph:
        s_can = s
        p_can = p
        o_can = o

        if not isinstance(p_can, URIRef) or str(p_can) not in allowed_predicates:
            continue

        if p_can == RDF.type and not str(o_can).startswith(TARGET_ONTOLOGY_NAMESPACE):
            continue

        if is_fusable(p_can):
            # Add exactly one value if none exists yet
            if not any(seed_graph.objects(s_can, p_can)):
                seed_graph.add((s_can, p_can, o_can))
                selected.append(
                    TrackRecord(subject=s_can,predicate=p_can,object=o,original_subject=s,original_predicate=p,original_object=o))
                # keep subjects set fresh for subsequent matches
                if isinstance(s_can, URIRef):
                    current_subjects.add(str(s_can))
            else:
                discarded.append(
                    TrackRecord(subject=s_can,predicate=p_can,object=o,original_subject=s,original_predicate=p,original_object=o))
        else:
            # Non-fusable: copy if not already present (avoid dupes)
            if (s_can, p_can, o_can) not in seed_graph:
                seed_graph.add((s_can, p_can, o_can))
                if isinstance(s_can, URIRef):
                    current_subjects.add(str(s_can))

    # sel(ected)
    selected_file_path = outputs["output"].path.parent / (outputs["output"].path.stem + ".selected.json")
    with open(selected_file_path, "w") as f:
        json.dump(selected, f, default=lambda x: x.model_dump())
    # dis(carded)
    discarded_file_path = outputs["output"].path.parent / (outputs["output"].path.stem + ".discarded.json")
    with open(discarded_file_path, "w") as f:
        json.dump(discarded, f, default=lambda x: x.model_dump())

    # prov graph is skipped here as no uris are replaced (is done in previouse steps)
    seed_graph.serialize(outputs["output"].path, format="nt")


# Demo harness (identical on both sides, see meta.json): `select_first_value`
# reads two graphs from N-Triples FILES and writes its result back to one,
# so `demo` builds a fresh, isolated temp directory per call, writes
# `source_nt`/`target_nt` there, sets `ONTOLOGY_PATH` to a tiny JSON
# ontology (see context_shim.OntologyUtil), runs the region, and returns
# the resulting graph parsed back from `outputs["output"].path` -- the
# comparable end state of every read/write this region performs, including
# both trav_existence reads (`any(seed_graph.objects(...))` and
# `(s, p, o) not in seed_graph`).
def demo(source_nt, target_nt, ontology_props=()):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        source_path = tmp / "source.nt"
        source_path.write_text(source_nt)
        target_path = tmp / "target.nt"
        target_path.write_text(target_nt)
        output_path = tmp / "output.nt"
        ontology_path = tmp / "ontology.json"
        ontology_path.write_text(json.dumps(list(ontology_props)))

        os.environ["ONTOLOGY_PATH"] = str(ontology_path)
        inputs = {"source": Data(path=source_path), "target": Data(path=target_path)}
        outputs = {"output": Data(path=output_path)}
        select_first_value(inputs, outputs)

        result = Graph()
        result.parse(output_path, format="nt")
        return result
