# Extracted from ternaustralia/vocview@006ad7b899 : skos/register.py
# region: Register._generate_dcat_html_metadata (lines 24-106, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, DCTERMS, XSD, RDFS, FOAF
from config import Config

def _generate_dcat_html_metadata(self):
    if 'http://www.w3.org/2004/02/skos/core#ConceptScheme' or 'http://www.w3.org/2004/02/skos/core#Collection' in \
            self.contained_item_classes:
        # If this register is rendering the view for skos:ConceptSchemes or skos:Collections,
        # then inject additional HTML.

        g = Graph()
        DCAT = Namespace('http://www.w3.org/ns/dcat#')

        # Catalog
        catalog = URIRef(self.request.base_url)
        g.add((catalog, RDF.type, DCAT.Catalog))
        g.add((catalog, DCTERMS.title, Literal(Config.title)))
        g.add((catalog, RDFS.label, Literal(Config.title)))
        g.add((catalog, DCTERMS.description, Literal(Config.description)))
        # g.add((catalog, FOAF.landingPage, catalog))
        g.add((catalog, FOAF.homepage, URIRef(self.request.url_root)))

        for item in self.register_items:
            # Dataset
            g.add((item[0], RDF.type, DCAT.Dataset))
            g.add((item[0], DCTERMS.title, item[1]))
            g.add((item[0], RDFS.label, item[1]))
            g.add((item[0], DCTERMS.type, URIRef('http://id.loc.gov/vocabulary/marcgt/dic')))
            g.add((item[0], DCAT.landingPage, URIRef('{}id/{}'.format(self.request.host_url, item[0]))))
            g.add((catalog, DCAT.dataset, item[0]))

            if item[2][0][1]:
                # dcterms:created
                g.add((item[0], item[2][0][0], Literal(item[2][0][1], datatype=XSD.date)))
            if item[2][1][1]:
                # dcterms:modified
                g.add((item[0], item[2][1][0], Literal(item[2][1][1], datatype=XSD.date)))
            if item[2][2] and item[2][2][1]:
                # dcterms:description
                g.add((item[0], item[2][2][0], item[2][2][1]))

            # Distribution
            subject = URIRef(self.request.host_url + '?_format=text/html&_view=skos')
            g.add((subject, RDF.type, DCAT.Distribution))
            g.add((subject, DCAT.downloadURL, subject))
            g.add((subject, DCAT.mediaType, URIRef('https://www.iana.org/assignments/media-types/text/html')))
            g.add((catalog, DCAT.distribution, subject))

            subject = URIRef(self.request.host_url + '?_format=text/turtle&_view=skos')
            g.add((subject, RDF.type, DCAT.Distribution))
            g.add((subject, DCAT.downloadURL, subject))
            g.add((subject, DCAT.mediaType, URIRef('https://www.iana.org/assignments/media-types/text/turtle')))
            g.add((catalog, DCAT.distribution, subject))

            subject = URIRef(self.request.host_url + '?_format=application/rdf+xml&_view=skos')
            g.add((subject, RDF.type, DCAT.Distribution))
            g.add((subject, DCAT.downloadURL, subject))
            g.add((subject, DCAT.mediaType,
                   URIRef('https://www.iana.org/assignments/media-types/application/rdf+xml')))
            g.add((catalog, DCAT.distribution, subject))

            subject = URIRef(self.request.host_url + '?_format=application/ld+json&_view=skos')
            g.add((subject, RDF.type, DCAT.Distribution))
            g.add((subject, DCAT.downloadURL, subject))
            g.add((subject, DCAT.mediaType,
                   URIRef('https://www.iana.org/assignments/media-types/application/ld+json')))
            g.add((catalog, DCAT.distribution, subject))

            subject = URIRef(self.request.host_url + '?_format=text/n3&_view=skos')
            g.add((subject, RDF.type, DCAT.Distribution))
            g.add((subject, DCAT.downloadURL, subject))
            g.add((subject, DCAT.mediaType,
                   URIRef('https://www.iana.org/assignments/media-types/text/n3')))
            g.add((catalog, DCAT.distribution, subject))

            subject = URIRef(self.request.host_url + '?_format=application/n-triples&_view=skos')
            g.add((subject, RDF.type, DCAT.Distribution))
            g.add((subject, DCAT.downloadURL, subject))
            g.add((subject, DCAT.mediaType,
                   URIRef('https://www.iana.org/assignments/media-types/application/n-triples')))
            g.add((catalog, DCAT.distribution, subject))

        additional_html = '<script type="application/ld+json">' + g.serialize(format='json-ld').decode('utf-8') + '</script>'
    else:
        additional_html = None

    return additional_html
