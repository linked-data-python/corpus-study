# Extracted from NextCenturyCorporation/AIDA-Interchange-Format@1197e7adef : python/aida_interchange/ldc_time_component.py
# region: LDCTimeComponent.make_aif_time_component (lines 47-60, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import XSD, Literal, URIRef
from shim import aifutils
from shim import interchange_ontology

def make_aif_time_component(self, g):
    """
    Creates a time component containing a Year, Month, and Day as well as a Type to clarify relative time

    :param LDCTimeComponent self: contains the time component information when LDCTimeComponent is instantiated
    :param rdflib.graph.Graph g: The underlying RDF model for the operation
    :returns: time_component node
    """
    time_component = aifutils._make_aif_resource(g, None, interchange_ontology.LDCTimeComponent, None)
    g.add((time_component, interchange_ontology.timeType, Literal(self.time_type.name, datatype=XSD.string)))
    self.add_literal(g, time_component, interchange_ontology.year, self.year, XSD.gYear)
    self.add_literal(g, time_component, interchange_ontology.month, self.month, XSD.gMonth)
    self.add_literal(g, time_component, interchange_ontology.day, self.day, XSD.gDay)
    return time_component
