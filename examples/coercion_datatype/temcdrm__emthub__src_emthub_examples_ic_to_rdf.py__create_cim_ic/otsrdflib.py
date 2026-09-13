# Context shim (see meta.json): OrderedTurtleSerializer from PyPI package
# otsrdflib v0.5.0 (otsrdflib/ots.py, github.com/scriptotek/otsrdflib), so
# the region executes without the real dependency. Identical bindings for
# both representations. Only the constructor and the attributes the region
# touches (class_order) matter here; orderSubjects/serialize are the real
# upstream logic, kept so the produced Turtle is unaffected by the shim.
import re

from rdflib.namespace import RDF
from rdflib.plugins.serializers.turtle import TurtleSerializer


class OrderedTurtleSerializer(TurtleSerializer):
    short_name = "ots"

    def __init__(self, store):
        super().__init__(store)
        self.class_order = []
        self.sorters_by_class = {}
        self.sorters = [('^(.+)$', lambda x: str(x[0]))]

    def getSorters(self, cls):
        return self.sorters_by_class.get(cls, self.sorters)

    def getSortKeyFunction(self, cls):
        for pattern, func in self.getSorters(cls):
            return func
        return lambda x: str(x[0])

    def orderSubjects(self):
        seen = set()
        subjects = []

        def class_of(subject):
            for _, _, o in self.store.triples((subject, RDF.type, None)):
                return o
            return None

        by_class: dict = {}
        others = []
        for s in self.store.subjects():
            if s in seen:
                continue
            seen.add(s)
            cls = class_of(s)
            if cls is None:
                others.append(s)
            else:
                by_class.setdefault(cls, []).append(s)

        ordered_classes = list(self.class_order)
        for cls in sorted(by_class, key=str):
            if cls not in ordered_classes:
                ordered_classes.append(cls)

        for cls in ordered_classes:
            members = by_class.get(cls, [])
            key = self.getSortKeyFunction(cls)
            members.sort(key=lambda s: key((s,)))
            subjects.extend(members)
        subjects.extend(sorted(others, key=str))
        return subjects
