# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/data_specification_iec_61360.py
# region: LangStringPreferredNameTypeIec61360.from_rdf (lines 56-65, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace

@staticmethod
def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
    language: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["AbstractLangString/language"]), None
    )
    text: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["AbstractLangString/text"]),
        None,
    )
    return LangStringPreferredNameTypeIec61360(language=language.value, text=text.value)
