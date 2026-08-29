# Extracted from BD2KOnFHIR/fhirtordf@05b23ba1df : tests/fhir_tests/test_fhir_ttl.py
# region: FHIRTTLTestCase.is_xsd_primitive (lines 12-31, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, RDFS, BNode, OWL, XSD, URIRef
from fhirtordf.rdfsupport.namespaces import FHIR

@staticmethod
def is_xsd_primitive(prim: URIRef, g: Graph) -> bool:
    for node in g.objects(prim, RDFS.subClassOf):
        if isinstance(node, BNode) and g.value(node, OWL.onProperty) == FHIR.value:
            # Older versions of fhir.ttl used allValuesFrom (incorrect, btw)
            base_type = g.value(node, OWL.allValuesFrom)
            if not base_type:
                base_node = g.value(node, OWL.someValuesFrom)
                if isinstance(base_node, BNode):
                    base_type = g.value(base_node, OWL.onDatatype)
            if not str(base_type).startswith(str(XSD)):
                print("type failure - {} : {}".format(prim, base_type))
                # TODO: Remove this once FHIRCat issue #35 (https://github.com/fhircat/FHIRCat/issues/35) is fixed
                if base_type == FHIR.integer64:
                    print("integer64 issue still needs fixing")
                else:
                    return False
            return True
    print("No base type defined for {}".format(prim))
    return False
