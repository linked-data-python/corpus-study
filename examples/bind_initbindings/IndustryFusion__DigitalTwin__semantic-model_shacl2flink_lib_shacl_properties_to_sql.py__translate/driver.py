"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_shacl2flink_lib_shacl_properties_to_sql.py__translate.

`translate` (restored as `def translate(g, prefixes):`, see original.py and
meta.json -- the region itself is a single statement, `g` and `prefixes`
being two of the three parameters of the real enclosing function) runs the
module's big SPARQL SELECT and sorts the rows; it neither builds nor mutates
a graph, so `g`/`prefixes` are call arguments the driver constructs, like
the Terramorpha__minergym precedent elsewhere in this stratum (no shim
module needed for those two -- only `lib/utils.py`, see meta.json).

The fixture graph satisfies exactly the query's non-OPTIONAL backbone: one
sh:NodeShape with a target class, a property with an own sh:minCount
(taking the "no connective" UNION arm), and a value shape whose sh:path is
ngsi-ld:hasValue (taking the FILTER on ?valuepath) -- this is also what
exercises `initNs`: `ngsi-ld:` is not one of rdflib's own default-bound
prefixes (`sh:`/`rdfs:`/`rdf:` are, checked empirically), so the FILTER
cannot even parse without `prefixes` supplying it.

meta.classification is not-expressible (see translated.ldpy): the region
was left as plain rdflib on both sides, so this driver's real job is
confirming that restoring the binding did not itself introduce a
difference, and that the check can actually fail (see the anti-hollow-green
note in the batch report) -- not exercising any island.
"""
from rdflib import Graph, Namespace

from rdfeval.harness import run_pair

FIXTURE = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .
@prefix ngsild: <https://uri.etsi.org/ngsi-ld/> .

ex:MyShape a sh:NodeShape ;
    sh:targetClass ex:MyClass ;
    sh:property ex:MyProperty .

ex:MyProperty sh:path ex:hasAttr ;
    sh:minCount 1 ;
    sh:property ex:ValueShape .

ex:ValueShape sh:path ngsild:hasValue .
"""


def _case():
    # Built fresh per side (a callable case, not a shared tuple): the region
    # only reads, but run_pair also compares each argument after the call,
    # and a Graph shared between sides would spuriously "differ" only in
    # identity if either side's rdflib internals touched it.
    g = Graph().parse(data=FIXTURE, format="turtle")
    prefixes = {"ngsi-ld": Namespace("https://uri.etsi.org/ngsi-ld/")}
    return (g, prefixes), {}


VERDICT = run_pair(
    __file__,
    entry="translate",
    calls=[_case],
)
