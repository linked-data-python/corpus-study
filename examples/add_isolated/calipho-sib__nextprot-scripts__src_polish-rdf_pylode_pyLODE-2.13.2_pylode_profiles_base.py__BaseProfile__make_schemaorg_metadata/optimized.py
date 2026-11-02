# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/base.py
# region: BaseProfile._make_schemaorg_metadata (lines 372-463, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import SDO, SKOS, OWL, URIRef, RDF, PROF, Literal, XSD, Graph, Namespace, FOAF, Graph

def _make_schemaorg_metadata(self):
    metadata = self.METADATA
    uri = URIRef(metadata.get("uri"))
    if metadata.get("modified") is not None:
        date_modified = Literal(metadata.get("modified"), datatype=XSD.date)
    license = None
    if metadata.get("license") is not None:
        if self.outputformat == "md":
            license = URIRef(metadata.get("license").split('(')[0].strip('[]'))
        elif self.outputformat == "adoc":
            license = URIRef(metadata.get("license").replace("link:", "").split("[")[0])
        else:
            license = URIRef(metadata.get("license").split('"')[1])
    if metadata.get("created") is not None:
        date_created = Literal(metadata.get("created"), datatype=XSD.date)
        copyright_year = Literal(metadata.get("created").split("-")[0], datatype=XSD.int)
    if metadata.get("repository") is not None:
        if self.outputformat == "adoc":
            repository = URIRef(metadata.get("repository").replace("link:", "").split("[")[0])
        else:
            repository = URIRef(metadata.get("repository").split('"')[1])

    """
    @prefix sdo: <https://schema.org/> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    <http://linked.data.gov.au/def/crs> a sdo:DigitalDocument ;
        sdo:name "CRS Ontology" ;
        sdo:publisher <http://catalogue.linked.data.gov.au/org/naa> ;
        sdo:creator [
            sdo:name "Nicholas J. Car" ;
            sdo:identifier <http://orcid.org/0000-0002-8742-7730> ;
            sdo:email <nicholas.car@csiro.au> ;
            sdo:memberOf [
                sdo:name "CSIRO" ;
                sdo:identifier <http://catalogue.linked.data.gov.au/org/csiro> ;
            ] ;
        ] ;
        sdo:date_created "2018-09-10"^^xsd:date ;
        sdo:date_modified "2019-05-31"^^xsd:date ;
        sdo:license <https://creativecommons.org/licenses/by/4.0/> ;

        sdo:copyrightHolder <http://catalogue.linked.data.gov.au/org/naa> ;
        sdo:copyright_year "2019"^^xsd:gYear ;
        sdo:encodingFormat <https://w3id.org/mediatype/text/html> ;
    .

    <http://catalogue.linked.data.gov.au/org/naa>
        a sdo:Organization ;
        sdo:name "National Archives of Australia" ;
        sdo:identifier <http://catalogue.linked.data.gov.au/org/naa> ;
    .        
    """
    g = Graph()
    SDO = Namespace("https://schema.org/")
    g.bind("sdo", SDO)
    g.bind("xsd", XSD)

    g += [(uri, RDF.type, SDO.DefinedTermSet), (uri, SDO.name, Literal(metadata.get("title")))]
    # g.add((uri, SDO.publishers, SDO.DigitalDocument))
    # g.add((uri, SDO.creators, SDO.DigitalDocument))
    if metadata.get("date_created") is not None:
        g.add((uri, SDO.dateCreated, date_created))
    if metadata.get("date_modified") is not None:
        g.add((uri, SDO.dateModified, date_modified))
    if metadata.get("description") is not None:
        g.add((uri, SDO.description, Literal(metadata.get("description"))))
    if license is not None:
        g.add((uri, SDO.license, license))
    if metadata.get("rights") is not None:
        g.add((uri, SDO.rights, Literal(metadata.get("rights"))))
    # g.add((uri, SDO.copyrightHolder, copyrightHolder))
    if metadata.get("copyright_year") is not None:
        g.add((uri, SDO.copyrightYear, copyright_year))
    if metadata.get("repository") is not None:
        g.add((uri, SDO.codeRepository, repository))

    return g.serialize(format="json-ld")
