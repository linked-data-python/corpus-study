# Extracted from OpenEnergyPlatform/oeplatform@ff28ef6390 : factsheet/views.py
# region: create_factsheet_view (lines 201-253, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import RDF, Graph, Literal, URIRef
from factsheet.oekg.namespaces import DC, OBO, OEKG, OEO, RDFS, XSD
from factsheet.utils import remove_non_printable, serialize_publication_date

for item in _publications:
    publications_URI = URIRef(
        "https://openenergyplatform.org/ontology/oekg/publication/" + item["id"]
    )
    # OEO_00020012
    bundle.add((publications_URI, OEO.OEO_00390095, Literal(item["id"])))
    bundle.add((publications_URI, RDF.type, OEO.OEO_00020012))
    bundle.add((study_URI, OBO.BFO_0000051, publications_URI))
    if item["report_title"] != "":
        bundle.add(
            (
                publications_URI,
                RDFS.label,
                Literal(remove_non_printable(item["report_title"])),
            )
        )

    _authors = item["authors"]
    for author in _authors:
        author_URI = URIRef(
            "https://openenergyplatform.org/ontology/oekg/" + author["iri"]
        )
        bundle.add((author_URI, RDF.type, OEO.OEO_00000064))
        bundle.add((publications_URI, OEO.OEO_00000506, author_URI))

    if item["doi"] != "":
        bundle.add((publications_URI, OEO.OEO_00390098, Literal(item["doi"])))

    if (
        item["date_of_publication"] != "01-01-1900"
        and item["date_of_publication"] != ""
    ):
        bundle.add(
            (
                publications_URI,
                OEO.OEO_00390096,
                Literal(item["date_of_publication"], datatype=XSD.dateTime),
            )
        )

    if item["link_to_study_report"] != "":
        bundle.add(
            (URIRef(item["link_to_study_report"]), RDF.type, OEO.OEO_00000353)
        )
        bundle.add(
            (
                publications_URI,
                OEO.OEO_00390078,
                URIRef(item["link_to_study_report"]),
            )
        )

    bundle.add((study_URI, OBO.BFO_0000051, publications_URI))
