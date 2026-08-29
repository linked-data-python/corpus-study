# Context shim (see meta.json): restores `H` and the `Graph`/`Namespace`
# imports that landscape/06-gates/semtech_supplementary_gates_v1_0_0.py
# declares at its own module top (lines 1-15 of the source file, not carried
# by the lines-149-151 extraction):
#
#   from rdflib import Graph, Namespace, URIRef, Literal
#   H = "/home/claude/semtech-landscape"
#
# `H` there is an absolute path specific to the source repository author's
# own machine (a "/home/claude/..." dev container), so it cannot resolve
# here as written. This shim points it instead at this corpus study's own
# checkout of the same source repository, commit bad0fa7c46 --
# corpus/repos/altunelyusuf__SemanticTechnologies/landscape -- which holds
# the exact same landscape/02-ontology/semtech_abox_v1_0_0.ttl the region
# parses. Identical bindings for both representations.
import pathlib

from rdflib import Graph, Namespace

H = str(pathlib.Path(__file__).resolve().parents[3] / "corpus" / "repos" /
        "altunelyusuf__SemanticTechnologies" / "landscape")
