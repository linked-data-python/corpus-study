# Context shim (see meta.json): the bindings NanopubClaim.__init__ imports
# from the nanopub package (Nanopublication/nanopub-py@05022dc4bc), reduced to
# what the region touches, plus a stand-in for the zero-argument ``super()``
# (the region is a constructor of ``class NanopubClaim(Nanopub)``; extracted
# on its own it is a module-level function, so CPython has no ``__class__``
# cell for it).
# Used IDENTICALLY by original.py and translated.ldpy.
import sys
from dataclasses import dataclass
from typing import Optional

from rdflib import Namespace

# nanopub/namespaces.py
HYCL = Namespace("http://purl.org/petapico/o/hycl#")

# nanopub/definitions.py
DUMMY_NANOPUB_URI = "http://purl.org/nanopub/temp/np"
DUMMY_NAMESPACE = Namespace(DUMMY_NANOPUB_URI + "/")


# nanopub/profile.py
class ProfileError(RuntimeError):
    """Error to be raised if profile is not setup correctly."""


@dataclass
class Profile:
    name: str = "Test User"
    orcid_id: str = "https://orcid.org/0000-0002-1825-0097"

    @property
    def agent_id(self) -> str:
        return self.orcid_id


# nanopub/nanopub_conf.py (subset of the fields the region assigns)
@dataclass
class NanopubConf:
    profile: Optional[Profile] = None
    add_prov_generated_time: bool = False
    add_pubinfo_generated_time: bool = True
    attribute_assertion_to_profile: bool = False
    attribute_publication_to_profile: bool = False


_UNSET = object()


class _SuperProxy:
    def __init__(self, target=_UNSET, **kwargs):
        if target is not _UNSET:
            self.__dict__["_target"] = target       # built by super() below
        else:                                       # the region's call
            self._target.super_init_kwargs = dict(kwargs)


def super():
    """Zero-argument super() stand-in bound to the caller's ``self``."""
    return _SuperProxy(sys._getframe(1).f_locals.get("self"))
