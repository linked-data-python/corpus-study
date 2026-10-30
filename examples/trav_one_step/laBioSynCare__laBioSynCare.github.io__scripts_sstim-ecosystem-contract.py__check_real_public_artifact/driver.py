"""Validation driver for laBioSynCare__laBioSynCare.github.io__scripts_sstim-ecosystem-contract.py__check_real_public_artifact.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  Each graph is built or parsed fresh for each side.

The fixture is part of the translation: it must hold several solutions of the
pattern the region reads, the zero-solution case, and neighbouring triples
that must NOT match.

check_real_public_artifact(artifact, label) needs a label string too, so
`calls=` supplies it explicitly -- the default single-graph call (`fixture=`
alone) does not apply here.  The repository passes a parsed Graph and a
file name (scripts/sstim-ecosystem-contract.py:1546), or the guard probe
below (line 985).  The result is the list of error messages, compared as a
multiset (the loops walk sets).

* calls 0-1 -- fixture.ttl under two labels: the agent-curator traversal
  (a verified self-curator, an agent without curator, an unverified curator),
  a verified relationship curator, a verified activity actor.
* call 2 -- fixture_edge.ttl: an UNVERIFIED relationship curator and
  activity actor (the errors that prove the second and third traversals),
  a literal curator, an activity without actor, and for each traversal a
  neighbour that shares two of its three terms: the right subject under
  another predicate (prov:used, prov:wasDerivedFrom, prov:wasAttributedTo,
  prov:wasInfluencedBy), and the right predicate on a subject of another
  type (eco:notAnActivity, eco:notARelationship, eco:seeAlsoActivity).
* call 3 -- an empty graph, label "" (falsy): the three "has no" errors,
  zero solutions everywhere.
* call 4 -- the repository's own guard probe (check_real_artifact_guard,
  lines 963-985, rebuilt verbatim): an implementation-owned subject, an
  agent and a relationship curated by an external IRI, an activity whose
  actor is that IRI, a second agent with no curator.
"""
from pathlib import Path

from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import PROV

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "fixture.ttl"
EDGE = HERE / "fixture_edge.ttl"

# scripts/sstim-ecosystem-contract.py:94-108
SSTIM = Namespace("https://w3id.org/sstim#")
ECO = Namespace("https://w3id.org/sstim/ecosystem#")
RECORD = "https://w3id.org/sstim/ecosystem-record/relationship/"
ACTIVITY = "https://w3id.org/sstim/ecosystem-record/activity/"


def call_label_a():
    return ((fixture_graph(FIXTURE), "aggregate-A"), {})


def call_label_b():
    return ((fixture_graph(FIXTURE), "aggregate-B"), {})


def call_edge():
    return ((fixture_graph(EDGE), "edge.ttl"), {})


def call_empty():
    return ((Graph(), ""), {})


def call_guard_probe():
    # check_real_artifact_guard, scripts/sstim-ecosystem-contract.py:963-985
    candidate = Graph()
    candidate.add((
        URIRef("https://w3id.org/sstim/implementation/bsclab/guard-probe"),
        RDF.type,
        SSTIM.SensoryStimulationImplementation,
    ))
    probe_relationship = URIRef(RECORD + "real-guard-probe")
    probe_activity = URIRef(ACTIVITY + "real-guard-probe")
    probe_agent = URIRef("https://w3id.org/sstim/specialist/real-guard-probe")
    unroutable_agent = URIRef(
        "https://w3id.org/sstim/specialist/nested/real-guard-probe"
    )
    external_actor = URIRef("https://example.net/unverified-curator")
    candidate.add((probe_agent, RDF.type, ECO.EcosystemAgent))
    candidate.add((probe_agent, PROV.wasAttributedTo, external_actor))
    candidate.add((unroutable_agent, RDF.type, ECO.EcosystemAgent))
    candidate.add((probe_relationship, RDF.type, ECO.EcosystemRelationship))
    candidate.add((probe_relationship, PROV.wasAttributedTo, external_actor))
    candidate.add((probe_activity, RDF.type, ECO.EngagementActivity))
    candidate.add((probe_activity, PROV.wasAssociatedWith, external_actor))
    return ((candidate, "real-guard-probe.ttl"), {})


VERDICT = run_pair(
    __file__,
    entry='check_real_public_artifact',
    fixture="fixture.ttl",
    calls=[call_label_a, call_label_b, call_edge, call_empty,
           call_guard_probe],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)
