# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/referable.py
# region: Referable.from_rdf (lines 88-158, stratum trav_one_step)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace
from app.models.has_extensions import HasExtensions
from app.models.lang_string_name_type import LangStringNameType
from app.models.lang_string_text_type import LangStringTextType

@staticmethod
def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
    # HasExtension
    hasExtension = HasExtensions.from_rdf(graph, subject)

    category_value = None
    category_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["Referable/category"]),
        None,
    )
    if category_ref:
        category_value = category_ref.value

    id_short_value = None
    id_short_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["Referable/idShort"]),
        None,
    )
    if id_short_ref:
        id_short_value = id_short_ref.value

    display_name_value = []
    for display_ref in graph.objects(subject=subject, predicate=AASNameSpace.AAS["Referable/displayName"]):
        lang_ref: rdflib.Literal = next(
            graph.objects(subject=display_ref, predicate=AASNameSpace.AAS["AbstractLangString/language"]), None
        )
        language_value = None
        if lang_ref:
            language_value = lang_ref.value

        text_ref: rdflib.Literal = next(
            graph.objects(subject=display_ref, predicate=AASNameSpace.AAS["AbstractLangString/text"]), None
        )

        text_value = None
        if text_ref:
            text_value = text_ref.value

        display_name_value.append(LangStringNameType(language=language_value, text=text_value))

    if len(display_name_value) == 0:
        display_name_value = None

    description_value = []
    for description_ref in graph.objects(subject=subject, predicate=AASNameSpace.AAS["Referable/description"]):
        lang_ref: rdflib.Literal = next(
            graph.objects(subject=description_ref, predicate=AASNameSpace.AAS["AbstractLangString/language"]), None
        )
        language_value = None
        if lang_ref:
            language_value = lang_ref.value

        text_ref: rdflib.Literal = next(
            graph.objects(subject=description_ref, predicate=AASNameSpace.AAS["AbstractLangString/text"]), None
        )

        text_value = None
        if text_ref:
            text_value = text_ref.value

        description_value.append(LangStringTextType(language=language_value, text=text_value))

    if len(description_value) == 0:
        description_value = None
    return Referable(
        category=category_value,
        idShort=id_short_value,
        displayName=display_name_value,
        description=description_value,
        extensions=hasExtension.extensions,
    )
