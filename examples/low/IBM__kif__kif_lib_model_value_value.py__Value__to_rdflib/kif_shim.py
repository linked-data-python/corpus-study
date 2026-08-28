# Context shim (see meta.json): minimal stand-ins for the kif_lib.model.value
# classes that Value._to_rdflib dispatches on, from IBM/kif@4ce99d0d9b
# (kif_lib/model/value/{entity,iri,quantity,string,text,time}.py).  Only the
# attributes the region reads are kept (Entity.iri, IRI.content,
# Quantity.amount, Time.time, Text.content/language, String.content) and the
# class hierarchy of the original is preserved (Text and String are siblings,
# Entity is not a data value).  Identical for both representations.


class Value:
    def _should_not_get_here(self):
        return RuntimeError('should not get here')


class Entity(Value):
    def __init__(self, iri):
        self.iri = iri


class IRI(Value):
    def __init__(self, content):
        self.content = content


class Quantity(Value):
    def __init__(self, amount):
        self.amount = amount


class String(Value):
    def __init__(self, content):
        self.content = content


class Text(Value):
    def __init__(self, content, language):
        self.content = content
        self.language = language


class Time(Value):
    def __init__(self, time):
        self.time = time
