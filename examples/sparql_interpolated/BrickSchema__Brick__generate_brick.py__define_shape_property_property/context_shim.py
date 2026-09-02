# Context shim (see meta.json): subset of BrickSchema/Brick@c12949f236 so the
# extracted region executes outside the package. `bricksrc.namespaces` binds
# the project's real namespace IRIs; `brickschema.Graph` is a thin subclass
# of rdflib.Graph in the real project, used here only as a default-argument
# constructor, so plain rdflib.Graph is an identical stand-in for both
# representations.
from rdflib import Namespace, Graph

BRICK = Namespace("https://brickschema.org/schema/Brick#")
BSH = Namespace("https://brickschema.org/schema/BrickShape#")
REC = Namespace("https://w3id.org/rec#")
from rdflib.namespace import RDF, OWL, RDFS
TAG = Namespace("https://brickschema.org/schema/BrickTag#")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
QUDT = Namespace("http://qudt.org/schema/qudt/")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
SH = Namespace("http://www.w3.org/ns/shacl#")
REF = Namespace("https://brickschema.org/schema/Brick/ref#")


class _BrickschemaShim:
    """Stand-in for the `brickschema` package: only `Graph` is used here,
    as a default-argument constructor, so plain rdflib.Graph is enough."""
    Graph = Graph


brickschema = _BrickschemaShim()


def add_relationships(ps, definitions, graph=None):
    """Stand-in for generate_brick.add_relationships (defined elsewhere in
    the same source file, outside this region): it refines a SHACL property
    shape from any relationship keys still left in `definitions` (e.g.
    "domain", "subproperty_of"). The driver's fixtures leave `definitions`
    empty by the time this is called (every key the region itself handles is
    popped first), so a no-op is behaviourally identical here for both
    representations without inventing logic this region does not exercise.
    """
    return
