# Context shim (see meta.json): BASEDIR, load(), nodes and cls_iri, restored
# from altunelyusuf/SemanticTechnologies@bad0fa7c46
# landscape/07-tooling/build_core_v6_3_0.py, lines 10-13, 34 and 41-43 --
# defined earlier in the same source file, just outside this region's
# extracted line range (162-163), and referenced by lines already in the
# captured context (IRI = {n["id"]: cls_iri(n) for n in nodes};
# g2 = Graph().parse(f"{BASEDIR}/...")). load() and cls_iri() are copied
# verbatim (cls_iri only reads "id" and "label", the two dict keys this
# shim's nodes carry). nodes is reduced to the 15 taxonomy entries
# en.NEW_RELATIONS actually references (T1C6, T3C1, T3C3, T3C5, T4C1, T4C2,
# T4C3, T4C4, T5C3, T5C5, T6C2, T6C3, T6C4, T9C3, T10C5), with their real
# id/label pairs copied verbatim from taxonomy_v1_0_0.py's TAX (the source
# builds nodes by flattening TAX's 12 top-level entries and their 47
# children; the other 44 leaf entries are never read by this region and are
# omitted -- so is "defn", which cls_iri does not use). BASEDIR's real value
# ("/home/claude/semtech-landscape", the original author's own machine) is
# redirected to this shim's own landscape/ subdirectory, holding a verbatim
# copy of enrichment_n_v6_0_0.py (the NEW_RELATIONS list this region
# iterates) and a minimal placeholder for semtech_tbox_v6_2_0.ttl (see that
# file's own header: this region never reads the pre-existing graph, only
# adds to it). Identical for both representations.
import os
import re
import importlib.util
from rdflib import Namespace

BASEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "landscape")

SEM = Namespace("http://example.org/semtech#")


def load(name, ver):
    s = importlib.util.spec_from_file_location(name, f"{BASEDIR}/07-tooling/{name}_{ver}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def cls_iri(n):
    return SEM[n["id"] + "_" + re.sub(r"[^A-Za-z0-9]+", "", n["label"])]


nodes = [
    {"id": "T1C6", "label": "Semantic Data Integration and Virtualization"},
    {"id": "T3C1", "label": "Enterprise Knowledge Graphs"},
    {"id": "T3C3", "label": "Data Fabric and Metadata Activation"},
    {"id": "T3C5", "label": "Master Data and Product Information Semantics"},
    {"id": "T4C1", "label": "Technology Sector Adoption"},
    {"id": "T4C2", "label": "Finance and Life Sciences Adoption"},
    {"id": "T4C3", "label": "Industrial and Manufacturing Adoption"},
    {"id": "T4C4", "label": "Retail and Fashion Adoption"},
    {"id": "T5C3", "label": "Semantic Layer Platforms"},
    {"id": "T5C5", "label": "Startups and Emerging Vendors"},
    {"id": "T6C2", "label": "Quality Assurance Techniques"},
    {"id": "T6C3", "label": "Ontology Design Patterns"},
    {"id": "T6C4", "label": "LLM-Assisted Ontology Engineering"},
    {"id": "T9C3", "label": "Visualization and Documentation Tools"},
    {"id": "T10C5", "label": "Academic Venues and Journals"},
]
