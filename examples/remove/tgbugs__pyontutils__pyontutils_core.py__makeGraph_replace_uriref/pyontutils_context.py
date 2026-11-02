# Context shim (see meta.json): subset of pyontutils/core.py from
# tgbugs/pyontutils@cb3efcd10f (class makeGraph), so the region executes
# outside the package: pyontutils is not installed in the study venv and its
# core module pulls in the whole ontology tool chain.  Reproduced verbatim:
# `expand`, `check_thing`, `add_trip`.  `__init__` is reduced to the two
# attributes the region reads (`g`, `namespaces`); the real one also binds the
# namespaces on the graph, which the caller does here.  Identical bindings for
# both representations.
import rdflib


class makeGraph:
    def __init__(self, graph, namespaces):
        self.g = graph
        self.namespaces = dict(namespaces)

    def expand(self, curie):
        if isinstance(curie, rdflib.URIRef):
            return curie

        prefix, suffix = curie.split(':', 1)
        if ' ' in prefix:
            raise ValueError(f'Namespace prefix {prefix!r} is not a valid curie prefix!')
        if prefix not in self.namespaces:
            raise KeyError(f'Namespace prefix {prefix} does not exist for {curie}')
        return self.namespaces[prefix][suffix]

    def check_thing(self, thing):
        if type(thing) == rdflib.Literal:
            return thing
        elif not isinstance(thing, rdflib.term.URIRef) and not isinstance(thing, rdflib.term.BNode):
            try:
                return self.expand(thing)
            except (KeyError, ValueError) as e:
                if thing.startswith('http') and ' ' not in thing:  # so apparently some values start with http :/
                    return rdflib.URIRef(thing)
                else:
                    raise e
        else:
            return thing

    def add_trip(self, subject, predicate, object_):
        if not object_:  # no empty object_s!
            return
        subject = self.check_thing(subject)
        predicate = self.check_thing(predicate)
        try:
            if object_.startswith(':') and ' ' in object_:  # not a compact repr AND starts with a : because humans are insane
                object_ = ' ' + object_
            object_ = self.check_thing(object_)
        except (AttributeError, KeyError, ValueError) as e:
            object_ = rdflib.Literal(object_)  # trust autoconv
        self.g.add( (subject, predicate, object_) )
