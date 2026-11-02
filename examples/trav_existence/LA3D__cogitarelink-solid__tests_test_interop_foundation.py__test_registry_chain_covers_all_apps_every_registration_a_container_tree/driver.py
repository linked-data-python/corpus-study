"""Validation driver for LA3D__cogitarelink-solid__tests_test_interop_foundation.py__test_registry_chain_covers_all_apps_every_registration_a_container_tree.

The region is a test: it returns nothing when it passes, and RAISES
AssertionError (with a message naming the registration) when a read of its
graph is empty or wrong.  Called once on a graph where every assertion
holds, it shows nothing (a hollow green).  What it computes is what its
assertions read, so this driver gives it that graph and, for each assertion,
a graph that falsifies exactly that one (the earlier ones keep holding).  A
raise is compared by type and message on both sides, and the messages quote
the registration or the tree read, so a translation that reads another term
is caught.

Each graph is `fixture.ttl` parsed fresh for each side, then edited by a
function of this file (the same on both sides).  This departs from the
original, which only ever sees the repository's own file, and the departure
is justified by the fact that the original shows nothing otherwise.

CALLS
  0. the fixture as it is: every assertion holds
  1. the owner has no hasRegistrySet                       -> assert 1
  2. the registry set has no hasDataRegistry               -> assert 2
  3. 11 registrations (one unlinked from the registry)     -> len == 12
  4. 13 registrations (the decoy linked in)                -> len == 12
  5. a registration whose tree does not end in ContainerTree -> loop assert
  6. a registration without registeredShapeTree            -> loop assert (None)
  7. 12 registrations but 8 wiki ones (a contacts one swapped for the decoy)
                                                           -> len(wiki) == 7
  8. a wiki registration pointing outside wiki-memory.tree -> startswith
  9..13. each of the five named registrations (contacts-person,
     -organization, -group, -membership, id-schemes) pointing at another
     ContainerTree                                         -> each `==`
A registration with TWO trees is not tried: `g.value` picks one of them
in an unspecified order, on both sides.
"""
from pathlib import Path

from rdflib import Namespace, URIRef

from rdfeval.harness import fixture_graph, run_pair

HERE = Path(__file__).resolve().parent
INTEROP = Namespace("http://www.w3.org/ns/solid/interop#")
REG = Namespace("https://pod.vardeman.me/vault/meta/interop/registry#")
WIKI = Namespace("https://pod.vardeman.me/vault/meta/shapetrees/wiki-memory.tree#")
AB = Namespace("https://pod.vardeman.me/vault/meta/shapetrees/addressbook.tree#")
IDT = Namespace("https://pod.vardeman.me/vault/meta/shapetrees/id-schemes.tree#")
OWNER = URIRef("https://pod.vardeman.me/vault/profile/card#me")
RSET = URIRef("urn:ex:rset1")
DREG = URIRef("urn:ex:dreg1")


def _graph(edit=None):
    def make():
        g = fixture_graph(HERE / "fixture.ttl")
        if edit is not None:
            edit(g)
        return (g,), {}
    return make


def _retree(registration, tree):
    def edit(g):
        g.remove((registration, INTEROP.registeredShapeTree, None))
        if tree is not None:
            g.add((registration, INTEROP.registeredShapeTree, tree))
    return edit


def _no_registry_set(g):
    g.remove((OWNER, INTEROP.hasRegistrySet, None))


def _no_data_registry(g):
    g.remove((RSET, INTEROP.hasDataRegistry, None))


def _eleven(g):
    g.remove((DREG, INTEROP.hasDataRegistration, REG.working))


def _thirteen(g):
    g.add((DREG, INTEROP.hasDataRegistration, REG.decoy))


def _eight_wiki(g):
    g.remove((DREG, INTEROP.hasDataRegistration, REG["contacts-membership"]))
    g.add((DREG, INTEROP.hasDataRegistration, REG.decoy))


VERDICT = run_pair(
    __file__,
    entry='test_registry_chain_covers_all_apps_every_registration_a_container_tree',
    calls=[
        _graph(),
        _graph(_no_registry_set),
        _graph(_no_data_registry),
        _graph(_eleven),
        _graph(_thirteen),
        _graph(_retree(REG.events, WIKI.EventsTree)),
        _graph(_retree(REG.places, None)),
        _graph(_eight_wiki),
        _graph(_retree(REG.people, AB.PeopleContainerTree)),
        _graph(_retree(REG["contacts-person"], AB.OrganizationContainerTree)),
        _graph(_retree(REG["contacts-organization"], AB.PersonContainerTree)),
        _graph(_retree(REG["contacts-group"], AB.MembershipContainerTree)),
        _graph(_retree(REG["contacts-membership"], AB.GroupContainerTree)),
        _graph(_retree(REG["id-schemes"], IDT.SchemeContainerTree)),
    ],
)
