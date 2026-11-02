# Context shim (see meta.json): the definitions the region uses and that the
# real script gives earlier in the file -- `load`, the `nodes` / `secnum`
# numbering loop and `cls_iri` -- copied verbatim from
# altunelyusuf/SemanticTechnologies@bad0fa7c46,
# landscape/06-gates/semtech_supplementary_gates_v6_6_0.py (lines 10-12 and
# 38-46), so the region executes outside that script.  HERE is this
# directory, which holds small stand-ins for the files the script finds under
# /home/claude/semtech-landscape.  Identical bindings for both representations.
import re, importlib.util
from pathlib import Path
from rdflib import Namespace

HERE = Path(__file__).resolve().parent
SEM = Namespace("http://example.org/semtech#")
def load(name, ver):
    s = importlib.util.spec_from_file_location(name, f"{HERE}/07-tooling/{name}_{ver}.py")
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
T = load("taxonomy", "v1_0_0")

order, secnum, nodes = [], {}, []
for i, t in enumerate(T.TAX, 1):
    nodes.append(t); order.append(t["id"]); secnum[t["id"]] = f"{i}"
    for j, c in enumerate(t["children"], 1):
        nodes.append(c); order.append(c["id"]); secnum[c["id"]] = f"{i}.{j}"
def cls_iri(n): return SEM[n["id"] + "_" + re.sub(r"[^A-Za-z0-9]+", "", n["label"])]
