# Extracted from johnjung/metadata_converters@36a81d6a97 : metadata_converters/ssmaps_edm.py
# region: SocSciMapsMarcXmlToEDM._build_cho (lines 135-213, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, DC, DCTERMS, XSD
BF      = Namespace('http://id.loc.gov/ontologies/bibframe/')
EDM     = Namespace('http://www.europeana.eu/schemas/edm/')
ERC     = Namespace('http://purl.org/kernel/elements/1.1/')
MADSRDF = Namespace('http://www.loc.gov/mads/rdf/v1#')

def _build_cho(self):
    """The cultural herigate object is the map itself. 

    This method adds triples that describe the cultural heritage object.

    Args:
        agg (URIRef): aggregation 
        cho (URIRef): cultural heritage object

    Side Effect:
        Add triples to self.graph
    """

    self.graph.add((self.cho, RDF.type, EDM.ProvidedCHO))
    for pre, obj_str in (
        (BF.ClassificationLcc,    '{http://id.loc.gov/ontologies/bibframe/}ClassificationLcc'),
        (BF.place,                '{http://id.loc.gov/ontologies/bibframe/}place'),
        (BF.scale,                '{http://id.loc.gov/ontologies/bibframe/}scale'),
        (DC.creator,              '{http://purl.org/dc/elements/1.1/}creator'),
        (DC.description,          '{http://purl.org/dc/elements/1.1/}description'),
        (DC.language,             '{http://purl.org/dc/elements/1.1/}language'),
        (DC.publisher,            '{http://purl.org/dc/elements/1.1/}publisher'),
        (DC.rights,               '{http://purl.org/dc/elements/1.1/}rights'),
        (DC.subject,              '{http://purl.org/dc/elements/1.1/}subject'),
        (DC.title,                '{http://purl.org/dc/elements/1.1/}title'),
        (DC.type,                 '{http://purl.org/dc/elements/1.1/}type'),
        (DCTERMS.dateCopyrighted, '{http://purl.org/dc/terms/}dateCopyrighted'),
        (DCTERMS.extent,          '{http://purl.org/dc/terms/}extent'),
        (DCTERMS.hasFormat,       '{http://purl.org/dc/terms/}hasFormat'),
        (DCTERMS.spatial,         '{http://purl.org/dc/terms/}spatial'),
        (ERC.what,                '{http://purl.org/dc/elements/1.1/}title'),
        (ERC.who,                 '{http://www.loc.gov/mads/rdf/v1#}ConferenceName'),
        (ERC.who,                 '{http://www.loc.gov/mads/rdf/v1#}CorporateName'),
        (ERC.who,                 '{http://www.loc.gov/mads/rdf/v1#}PersonalName'),
        (MADSRDF.ConferenceName,  '{http://www.loc.gov/mads/rdf/v1#}ConferenceName'),
        (MADSRDF.CorporateName,   '{http://www.loc.gov/mads/rdf/v1#}CorporateName'),
        (MADSRDF.PersonalName,    '{http://www.loc.gov/mads/rdf/v1#}PersonalName')
    ):
        for dc_obj_el in self.dc._asxml().findall(obj_str):
            self.graph.add((self.cho, pre, Literal(dc_obj_el.text)))

    # regarding the use of Literal() on the next line, instead of
    # URIRef()- as per a Slack message with Charles on March 29,
    # 2022: ...the value of dcterms:identifier in SSMAPS needs to be
    # a string: "Recommended practice is to identify the resource by
    # means of a string conforming to an identification system.
    # Examples include International Standard Book Number (ISBN),
    # Digital Object Identifier (DOI), and Uniform Resource Name
    # (URN). Persistent identifiers should be provided as HTTP
    # URIs." As I read the preceding, dcterms:identifier
    # <https://n2t.net/ark:61001/b2kg6jc39417> should be
    # dcterms:identifier "https://n2t.net/ark:61001/b2kg6jc39417".
    self.graph.add((self.cho, DCTERMS.identifier, Literal('https://n2t.net/{}'.format(self.ark))))
    self.graph.add((self.cho, DCTERMS.rights,     URIRef('https://rightsstatements.org/vocab/NoC-US/1.0/')))
    self.graph.add((self.cho, ERC.where,          URIRef('https://ark.lib.uchicago.edu/{}'.format(self.ark))))

    for dc_obj_el in self.dc._asxml().findall('{http://id.loc.gov/ontologies/bibframe/}Local'):
        self.graph.add((self.cho, BF.Local, URIRef(dc_obj_el.text)))

    d = []
    for f in self.digital_record.get_fields('260', '264'):
        for sf in f.get_subfields('c'):
            d.append(sf)
    if d:
        self.graph.add((self.cho, DC.date, Literal(process_date_string(d[0]))))
        self.graph.add((self.cho, EDM.year, Literal(process_date_string(d[0]))))
        self.graph.add((self.cho, ERC.when, Literal(process_date_string(d[0]))))

    # dc:format
    for dc_obj_el in self.dc._asxml().findall('{http://purl.org/dc/elements/1.1/}format'):
        self.graph.add((
            self.cho, 
            URIRef('http://purl.org/dc/elements/1.1/format'),
            Literal(dc_obj_el.text)
        ))

    self.graph.add((self.cho, EDM.currentLocation, Literal('Map Collection Reading Room (Room 370)')))

    self.graph.add((self.cho, EDM.type, Literal('IMAGE')))
