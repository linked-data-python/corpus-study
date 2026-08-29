# Extracted from sebneu/portalwatch@a514eba7bf : converter/dataset_converter.py
# region: CKANConverter.graph_from_ckan (lines 684-759, stratum coercion_datatype)
# licence of the source repository: see meta.json
import hashlib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, SKOS, RDFS
DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
ADMS = Namespace("http://www.w3.org/ns/adms#")

for resource_dict in dataset_dict.get('resources', []):
    distribution = URIRef(self.resource_uri(resource_dict, dataset_dict.get('id')))

    g.add((dataset_ref, DCAT.distribution, distribution))
    g.add((distribution, RDF.type, DCAT.Distribution))

    # License
    if license:
        g.add((distribution, DCT.license, license))


    #  Simple values
    items = [
        ('name', DCT.title, None),
        ('description', DCT.description, None),
        ('status', ADMS.status, None),
        ('rights', DCT.rights, None),
        ('license', DCT.license, None),
    ]

    _add_triples_from_dict(self.g, resource_dict, distribution, items)

    # Format
    if '/' in resource_dict.get('format', ''):
        g.add((distribution, DCAT.mediaType,
               Literal(resource_dict['format'])))
    else:
        if resource_dict.get('format'):
            id_string = dataset_ref.n3() + DCT['format'].n3() + resource_dict['format']
            bnode_hash = hashlib.sha1(id_string.encode('utf-8'))
            f = BNode(bnode_hash.hexdigest())

            g.add((f, RDF.type, DCT.MediaTypeOrExtent))
            g.add((f, RDFS.label, Literal(resource_dict['format'])))
            g.add((distribution, DCT['format'], f))
            if resource_dict.get('mimetype'):
                g.add((f, RDF.value, Literal(resource_dict['mimetype'])))

        if resource_dict.get('mimetype'):
            g.add((distribution, DCAT.mediaType,
                   Literal(resource_dict['mimetype'])))

    # URL
    url = resource_dict.get('url')
    download_url = resource_dict.get('download_url')
    if download_url:
        download_url = download_url.strip()
        if is_valid_uri(download_url):
            g.add((distribution, DCAT.downloadURL, URIRef(download_url)))
        else:
            g.add((distribution, DCAT.downloadURL, Literal(download_url)))
    if (url and not download_url) or (url and url != download_url):
        url = url.strip()
        if is_valid_uri(url):
            g.add((distribution, DCAT.accessURL, URIRef(url)))
        else:
            g.add((distribution, DCAT.accessURL, Literal(url)))
    # Dates
    # metadata-date was added as "most frequent extra key"
    items = [
        ('issued', DCT.issued, ['created',
                                'metadata-date']),
        ('modified', DCT.modified, ['last_modified']),
    ]

    _add_date_triples_from_dict(self.g, resource_dict, distribution, items)

    # Numbers
    if resource_dict.get('size'):
        try:
            g.add((distribution, DCAT.byteSize,
                   Literal(float(resource_dict['size']),
                           datatype=XSD.decimal)))
        except (ValueError, TypeError):
            g.add((distribution, DCAT.byteSize,
                   Literal(resource_dict['size'])))
