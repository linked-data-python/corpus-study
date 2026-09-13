# Context shim (see meta.json): subset of scripts/weaviate_utils.py from
# eliozo/worksheet-generation-with-llms@c065efff55, so the region -- a
# method that reads self.eliozoNS, self.client, self.skipping_mode -- can
# be called outside the WeaviateUtils class. The fake client records what
# would have been inserted into Weaviate (`self.inserted`) instead of
# connecting anywhere; `__eq__` compares on that, which is what makes the
# recorded `data_object` observable to the driver's equivalence check
# (the region's return value is a fixed status tuple, not the data).
# Identical bindings for both representations.
from rdflib import Namespace

ELIOZO_NS = Namespace("http://www.dudajevagatve.lv/eliozo#")


class _FakeData:
    def __init__(self, owner):
        self._owner = owner

    def insert(self, properties, references):
        self._owner.inserted.append(dict(properties))


class _FakeCollection:
    def __init__(self, owner):
        self._owner = owner

    @property
    def data(self):
        return _FakeData(self._owner)


class _FakeCollections:
    def __init__(self, owner):
        self._owner = owner

    def get(self, name):
        return _FakeCollection(self._owner)


class _FakeClient:
    def __init__(self, owner):
        self._owner = owner

    def is_ready(self):
        return True

    @property
    def collections(self):
        return _FakeCollections(self._owner)


class _Self:
    def __init__(self, skipping_mode=False):
        self.eliozoNS = ELIOZO_NS
        self.skipping_mode = skipping_mode
        self.inserted = []
        self.client = _FakeClient(self)

    def __eq__(self, other):
        return isinstance(other, _Self) and self.inserted == other.inserted

    def __repr__(self):
        return f"_Self(inserted={self.inserted!r})"


def make_self(skipping_mode=False):
    return _Self(skipping_mode=skipping_mode)
