# Extracted from OpenEnergyPlatform/oeplatform@ff28ef6390 : factsheet/views.py
# region: create_factsheet_view (lines 201-253, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import RDF, Literal, URIRef
from context_shim import OBO, OEO, RDFS, XSD, remove_non_printable, _publications, bundle, study_URI

for item in _publications:
    publications_URI = URIRef(
        "https://openenergyplatform.org/ontology/oekg/publication/" + item["id"]
    )
    # OEO_00020012
    bundle += [(publications_URI, OEO.OEO_00390095, Literal(item["id"])),
               (publications_URI, RDF.type, OEO.OEO_00020012),
               (study_URI, OBO.BFO_0000051, publications_URI)]
    if item["report_title"] != "":
        bundle.add((publications_URI, RDFS.label,
                    Literal(remove_non_printable(item["report_title"]))))

    for author in item["authors"]:
        author_URI = URIRef("https://openenergyplatform.org/ontology/oekg/" + author["iri"])
        bundle += [(author_URI, RDF.type, OEO.OEO_00000064),
                   (publications_URI, OEO.OEO_00000506, author_URI)]

    if item["doi"] != "":
        bundle.add((publications_URI, OEO.OEO_00390098, Literal(item["doi"])))

    if item["date_of_publication"] not in ("01-01-1900", ""):
        bundle.add((publications_URI, OEO.OEO_00390096,
                    Literal(item["date_of_publication"], datatype=XSD.dateTime)))

    if item["link_to_study_report"] != "":
        bundle += [(URIRef(item["link_to_study_report"]), RDF.type, OEO.OEO_00000353),
                   (publications_URI, OEO.OEO_00390078, URIRef(item["link_to_study_report"]))]
