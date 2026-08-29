# Extracted from mhrimaz/aasbrain-concept-description-repo@46ae59a87e : app/models/data_specification_iec_61360.py
# region: DataSpecificationIec61360.from_rdf (lines 330-440, stratum trav_one_step)
# licence of the source repository: see meta.json
import rdflib
from app.models.aas_namespace import AASNameSpace
from app.models.reference import Reference

@staticmethod
def from_rdf(graph: rdflib.Graph, subject: rdflib.IdentifiedNode):
    # TODO: !
    pref_name_langs = []
    for lang in graph.objects(
        subject=subject, predicate=AASNameSpace.AAS["DataSpecificationIec61360/preferredName"]
    ):
        pref_name_langs.append(LangStringPreferredNameTypeIec61360.from_rdf(graph, lang))

    short_name_langs = []
    for lang in graph.objects(subject=subject, predicate=AASNameSpace.AAS["DataSpecificationIec61360/shortName"]):
        short_name_langs.append(LangStringShortNameTypeIec61360.from_rdf(graph, lang))
    if len(short_name_langs) == 0:
        short_name_langs = None

    unit = None
    unit_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["DataSpecificationIec61360/unit"]),
        None,
    )
    if unit_ref:
        unit = unit_ref.value

    unit_id = None
    unit_id_ref: rdflib.URIRef = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["DataSpecificationIec61360/unitId"]),
        None,
    )
    if unit_id_ref:
        unit_id = Reference.from_rdf(graph, unit_id_ref)

    source_of_def = None
    source_of_def_ref: rdflib.Literal = next(
        graph.objects(subject=subject, predicate=AASNameSpace.AAS["DataSpecificationIec61360/sourceOfDefinition"]),
        None,
    )
    if source_of_def_ref:
        source_of_def = source_of_def_ref.value

    symbol = None
    symbol_ref: rdflib.Literal = next(
        graph.objects(
            subject=subject,
            predicate=AASNameSpace.AAS["DataSpecificationIec61360/symbol"],
        ),
        None,
    )
    if symbol_ref:
        symbol = symbol_ref.value

    deta_type = None
    deta_type_ref: rdflib.URIRef = next(
        graph.objects(
            subject=subject,
            predicate=AASNameSpace.AAS["DataSpecificationIec61360/dataType"],
        ),
        None,
    )
    if deta_type_ref:
        deta_type = DataTypeIec61360[deta_type_ref[deta_type_ref.rfind("/") + 1 :]]

    defintion_langs = []
    for lang in graph.objects(subject=subject, predicate=AASNameSpace.AAS["DataSpecificationIec61360/definition"]):
        defintion_langs.append(LangStringDefinitionTypeIec61360.from_rdf(graph, lang))

    if len(defintion_langs) == 0:
        defintion_langs = None

    value_format = None
    value_format_ref: rdflib.Literal = next(
        graph.objects(
            subject=subject,
            predicate=AASNameSpace.AAS["DataSpecificationIec61360/valueFormat"],
        ),
        None,
    )
    if value_format_ref:
        value_format = value_format_ref.value
    value = None
    value_ref: rdflib.Literal = next(
        graph.objects(
            subject=subject,
            predicate=AASNameSpace.AAS["DataSpecificationIec61360/value"],
        ),
        None,
    )
    if value_ref:
        value = value_ref.value
    level_type_ref: rdflib.URIRef = next(
        graph.objects(
            subject=subject,
            predicate=AASNameSpace.AAS["DataSpecificationIec61360/levelType"],
        ),
        None,
    )
    level_type = None
    if level_type_ref:
        level_type = LevelType.from_rdf(graph, level_type_ref)
    return DataSpecificationIec61360(
        preferredName=pref_name_langs,
        shortName=short_name_langs,
        unit=unit,
        unitId=unit_id,
        sourceOfDefinition=source_of_def,
        symbol=symbol,
        dataType=deta_type,
        definition=defintion_langs,
        valueFormat=value_format,
        value=value,
        levelType=level_type,
    )
