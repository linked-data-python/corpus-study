# Extracted from IBM/kif@4ce99d0d9b : kif_lib/model/value/value.py
# region: Value._to_rdflib (lines 239-259, band low)
# licence of the source repository: see meta.json
import namespace as NS
from rdflib import Literal, URIRef

def _to_rdflib(self) -> Literal | URIRef:
    from kif_shim import Entity
    from kif_shim import IRI
    from kif_shim import Quantity
    from kif_shim import String
    from kif_shim import Text
    from kif_shim import Time
    if isinstance(self, Entity):
        return URIRef(self.iri.content)
    elif isinstance(self, IRI):
        return URIRef(self.content)
    elif isinstance(self, Quantity):
        return Literal(str(self.amount), datatype=NS.XSD.decimal)
    elif isinstance(self, Time):
        return Literal(self.time.isoformat(), datatype=NS.XSD.dateTime)
    elif isinstance(self, Text):
        return Literal(self.content, self.language)
    elif isinstance(self, String):
        return Literal(self.content)
    else:
        raise self._should_not_get_here()
