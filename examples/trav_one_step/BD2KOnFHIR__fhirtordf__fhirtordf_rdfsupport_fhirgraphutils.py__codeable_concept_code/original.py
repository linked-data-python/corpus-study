# Extracted from BD2KOnFHIR/fhirtordf@05b23ba1df : fhirtordf/rdfsupport/fhirgraphutils.py
# region: codeable_concept_code (lines 100-132, stratum trav_one_step)
# licence of the source repository: see meta.json
from typing import Union, Optional, Tuple, List
from rdflib import Graph, BNode, Literal, RDF
from rdflib.term import Identifier, URIRef, Node
from fhirgraphutils_context import FHIR, value, CodeableConcept

def codeable_concept_code(g: Graph, subject: Node, predicate: URIRef, system: Optional[str]=None) \
        -> List[CodeableConcept]:
    """
    Return a list of CodeableConcept entries for the supplied subject and predicate in graph g
    :param g: graph containing the data
    :param subject: subject
    :param predicate: predicate
    :param system: coding system.  If present, only concepts in this system will be returned
    :return: system, code and optional URI of matching concept(s)
    """
    # EXAMPLE:
    # fhir:Patient.maritalStatus [
    #    fhir:CodeableConcept.coding [
    #      fhir:index 0;
    #      a sct:36629006;
    #      fhir:Coding.system [ fhir:value "http://snomed.info/sct" ];
    #      fhir:Coding.code [ fhir:value "36629006" ];
    #      fhir:Coding.display [ fhir:value "Legally married" ]
    #    ], [
    #      fhir:index 1;
    #      fhir:Coding.system [ fhir:value "http://hl7.org/fhir/v3/MaritalStatus" ];
    #      fhir:Coding.code [ fhir:value "M" ]
    #    ]
    # ];
    rval = []
    coded_entry = g.value(subject, predicate, any=False)
    if coded_entry:
        for codeable_concept in list(g.objects(coded_entry, FHIR.CodeableConcept.coding)):
            coding_system = value(g, codeable_concept, FHIR.Coding.system)
            coding_code = value(g, codeable_concept, FHIR.Coding.code)
            if coding_system and coding_code and (system is None or system == coding_system):
                rval.append(CodeableConcept(coding_system, coding_code, g.value(codeable_concept, RDF.type, any=False)))
    return rval
