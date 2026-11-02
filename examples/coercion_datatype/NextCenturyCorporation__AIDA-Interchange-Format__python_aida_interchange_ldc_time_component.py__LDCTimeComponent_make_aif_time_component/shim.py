# Context shim (see meta.json): the parts of NextCenturyCorporation/
# AIDA-Interchange-Format@1197e7adef (python/aida_interchange) that the region
# reaches, so it executes without the aida_interchange package (not installed
# in the study venv). Identical bindings for both representations.
#
#  - interchange_ontology   rdf_ontologies/interchange_ontology.py (generated
#                           file): NAMESPACE and the five terms the region uses
#  - aifutils               aifutils.py: _make_aif_resource, verbatim
#  - LDCTimeType, LDCTimeComponent (__init__, add_literal)
#                           ldc_time_component.py, verbatim, WITHOUT
#                           make_aif_time_component (the region)
from enum import Enum
from types import SimpleNamespace

from rdflib import RDF, BNode, Literal, URIRef

NAMESPACE = 'https://raw.githubusercontent.com/NextCenturyCorporation/AIDA-Interchange-Format/master/java/src/main/resources/com/ncc/aif/ontologies/InterchangeOntology#'

interchange_ontology = SimpleNamespace(
    NAMESPACE=NAMESPACE,
    LDCTimeComponent=URIRef(NAMESPACE + 'LDCTimeComponent'),
    day=URIRef(NAMESPACE + 'day'),
    month=URIRef(NAMESPACE + 'month'),
    timeType=URIRef(NAMESPACE + 'timeType'),
    year=URIRef(NAMESPACE + 'year'),
)


def _make_aif_resource(g, uri, class_type, system):
    """
    Helper function to create an event, relation, justification, etc. in the system.
    """
    if uri is None:
        resource = BNode()
    else:
        resource = URIRef(uri)
    g.add((resource, RDF.type, class_type))
    if system is not None:
        raise NotImplementedError("mark_system is not used by the region")
    return resource


aifutils = SimpleNamespace(_make_aif_resource=_make_aif_resource)


class LDCTimeType(Enum):
    """
    Enumeration of time types
    """
    ON = 1
    BEFORE = 2
    AFTER = 3
    UNKNOWN = 4


class LDCTimeComponent:
    """
    This class encapsulates the LDC representation of time
    """

    def __init__(self, time_type, year, month, day):
        self.time_type = time_type
        self.year = year
        self.month = month
        self.day = day

    def add_literal(self, g, time_component, time_property, value, literal_type):
        """
        Creates and adds a Literal to the model if a value exists
        """
        if value is not None:
            temp_literal = Literal(value)
            temp_literal._datatype = URIRef(literal_type)
            g.add((time_component, time_property, temp_literal))
