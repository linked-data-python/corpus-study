# Context shim (see meta.json).  The region is ``ProfilesDataset.__init__``
# from pylode/profiles/supermodel/loader.py (RDFLib/pyLODE@0d0471fb99), a
# method of ``class ProfilesDataset(Dataset)``.  Extracted on its own it is a
# module-level function, so CPython's zero-argument ``super()`` has no
# ``__class__`` cell and cannot run.  Importing the name ``super`` from here
# shadows the builtin with a stand-in that plays the one role the region
# needs: ``super().__init__(default_union=True)`` records the base-class
# initialisation on the caller's ``self``.
# Used IDENTICALLY by original.py and translated.ldpy.
import sys

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
