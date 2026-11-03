# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/referable.py
# region: Referable.from_rdf (lines 88-158, stratum trav_one_step)
# licence of the source repository: see meta.json
import rdflib
from shim import AASNameSpace, HasExtensions, LangStringNameType, LangStringTextType, Referable

@staticmethod
def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
    def value(node, local_name):
        ref = graph.value(node, AASNameSpace.AAS[local_name])
        return ref.value if ref else None

    def lang_strings(local_name, lang_string_type):
        return [
            lang_string_type(
                language=value(ref, "AbstractLangString/language"),
                text=value(ref, "AbstractLangString/text"),
            )
            for ref in graph.objects(subject, AASNameSpace.AAS[local_name])
        ] or None

    # HasExtension
    hasExtension = HasExtensions.from_rdf(graph, subject)
    return Referable(
        category=value(subject, "Referable/category"),
        idShort=value(subject, "Referable/idShort"),
        displayName=lang_strings("Referable/displayName", LangStringNameType),
        description=lang_strings("Referable/description", LangStringTextType),
        extensions=hasExtension.extensions,
    )
