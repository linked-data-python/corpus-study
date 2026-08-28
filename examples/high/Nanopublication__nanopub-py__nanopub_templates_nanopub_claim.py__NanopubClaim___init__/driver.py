"""Validation driver for NanopubClaim.__init__.

The region is a constructor of ``NanopubClaim(Nanopub)``.  The stub below
plays ``self`` with the same shape as the real base class: ``assertion``
and ``provenance`` are READ-ONLY properties over two named graphs (that is
why the ldpy side has to call ``__iadd__`` explicitly instead of ``+=``),
``_metadata.namespace`` is the dummy nanopub namespace, and ``profile``
carries an ORCID agent id.

Only the happy path is exercised: the ``not self.profile`` branch raises
ProfileError, which the harness would report as an execution error rather
than as a comparison.
"""
from rdflib import Graph

from nanopub_context import DUMMY_NAMESPACE, NanopubConf, Profile

from rdfeval.harness import run_pair


class _Metadata:
    namespace = DUMMY_NAMESPACE


class _Nanopub:
    """Stand-in for nanopub.Nanopub (the region's ``self``)."""

    def __init__(self, profile):
        self._assertion = Graph(identifier=DUMMY_NAMESPACE["assertion"])
        self._provenance = Graph(identifier=DUMMY_NAMESPACE["provenance"])
        self._metadata = _Metadata()
        self.profile = profile
        self.super_init_kwargs = None

    # the real class exposes these as read-only properties
    @property
    def assertion(self):
        return self._assertion

    @property
    def provenance(self):
        return self._provenance

    def __eq__(self, other):
        from rdflib.compare import to_isomorphic
        return (isinstance(other, _Nanopub)
                and self.super_init_kwargs == other.super_init_kwargs
                and to_isomorphic(self._assertion)
                == to_isomorphic(other._assertion)
                and to_isomorphic(self._provenance)
                == to_isomorphic(other._provenance))

    def __repr__(self):
        return "_Nanopub(assertion=%d, provenance=%d)" % (
            len(self._assertion), len(self._provenance))


def case(claim, orcid="https://orcid.org/0000-0002-1825-0097"):
    def make():
        profile = Profile(orcid_id=orcid)
        return ((_Nanopub(profile), claim, NanopubConf(profile=profile)), {})
    return make


VERDICT = run_pair(
    __file__,
    entry="__init__",
    calls=[
        case("All cats are grey"),
        case('A claim with "quotes", a newline\nand a \\ backslash'),
        case("Les chats sont gris", orcid="https://orcid.org/0000-0001-9236-4353"),
    ],
)
