# Context shim (see meta.json): the bricksrc.namespaces constants this
# region imports (verbatim values from BrickSchema/Brick@c12949f236
# bricksrc/namespaces.py) plus a stand-in for the top-level `brickschema`
# module: the extraction pipeline's context window captured `G =
# brickschema.Graph()` (module scope, line 73 of generate_brick.py) but not
# `import brickschema` (line 4) -- the missing binding is restored here per
# AGENT_BATCH.md, since 163/1196 regions in this study need exactly this.
# brickschema.Graph is itself a subclass of rdflib.Graph that adds
# ontology-loading/SHACL machinery this region never calls (it only uses
# .add/.query, inherited from rdflib.Graph unchanged); a full dependency on
# the `brickschema` package is unnecessary and out of scope for a minimal
# shim. Identical bindings for both representations.
import types

from rdflib import Graph, Namespace

BRICK = Namespace("https://brickschema.org/schema/Brick#")
TAG = Namespace("https://brickschema.org/schema/BrickTag#")
BSH = Namespace("https://brickschema.org/schema/BrickShape#")
REF = Namespace("https://brickschema.org/schema/Brick/ref#")
SH = Namespace("http://www.w3.org/ns/shacl#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
REC = Namespace("https://w3id.org/rec#")
QUDT = Namespace("http://qudt.org/schema/qudt/")


class _BrickschemaGraph(Graph):
    """Minimal stand-in for brickschema.Graph, unused ontology-loading
    behaviour aside (this region only calls .add()/.query(), inherited
    unchanged from rdflib.Graph)."""


brickschema = types.SimpleNamespace(Graph=_BrickschemaGraph)
