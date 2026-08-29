# Extracted from biosimulators/Biosimulators_utils@0176adc6c1 : biosimulators_utils/omex_meta/io.py
# region: BiosimulationsOmexMetaWriter.run (lines 809-890, stratum coercion_datatype)
# licence of the source repository: see meta.json
from .data_model import (Triple, OmexMetadataOutputFormat, OmexMetadataSchema,
                         BIOSIMULATIONS_ROOT_URI_PATTERN,
                         BIOSIMULATIONS_PREDICATE_TYPES,
                         BIOSIMULATIONS_NAMESPACE_PREFIX_MAP,
                         BIOSIMULATIONS_NAMESPACE_ALIASES)
from .utils import get_local_combine_archive_content_uri, get_global_combine_archive_content_uri
import rdflib

for predicate_type in BIOSIMULATIONS_PREDICATE_TYPES.values():
    namespace = namespaces[predicate_type['namespace']['prefix']]
    predicate = getattr(namespace, predicate_type['uri'].replace(predicate_type['namespace']['uri'], ''))

    if predicate_type['multiple_allowed']:
        values = el_metadata.get(predicate_type['attribute'], [])
    else:
        value = el_metadata.get(predicate_type['attribute'], None)
        if value is None:
            values = []
        else:
            values = [value]

    for value in values:
        if predicate_type['has_uri'] and predicate_type['has_label']:
            local_id += 1
            object = rdflib.term.URIRef('local:{:05d}'.format(local_id))

            if value.get('uri', None) is not None:
                triples.append(Triple(
                    object,
                    namespaces['dc'].identifier,
                    rdflib.term.URIRef(value['uri'])
                ))

            if value.get('label', None) is not None:
                triples.append(Triple(
                    object,
                    namespaces['rdfs'].label,
                    rdflib.term.Literal(value['label'])
                ))

            if predicate_type['uri'] in [
                'http://purl.org/dc/elements/1.1/creator',
                'http://purl.org/dc/elements/1.1/contributor',
            ]:
                if value.get('uri', None) is not None:
                    if value['uri'].lower().startswith('mailto:'):
                        triples.append(Triple(
                            object,
                            namespaces['foaf'].mbox,
                            rdflib.term.URIRef(value['uri'])
                        ))
                    if value['uri'].lower().startswith('tel:'):
                        triples.append(Triple(
                            object,
                            namespaces['foaf'].phone,
                            rdflib.term.URIRef(value['uri'])
                        ))
                    else:
                        triples.append(Triple(
                            object,
                            namespaces['foaf'].accountName,
                            rdflib.term.URIRef(value['uri']
                                               .replace('http://identifiers.org/orcid:',
                                                        'https://orcid.org/')
                                               .replace('https://identifiers.org/orcid:',
                                                        'https://orcid.org/')
                                               )
                        ))

                if value.get('label', None) is not None:
                    triples.append(Triple(
                        object,
                        namespaces['foaf'].name,
                        rdflib.term.Literal(value['label'])
                    ))

        elif predicate_type['has_uri']:
            if predicate_type['uri'] == 'http://www.collex.org/schema#thumbnail':
                value = get_global_combine_archive_content_uri(value, el_metadata['combine_archive_uri'])

            object = rdflib.term.URIRef(value)

        else:
            object = rdflib.term.Literal(value)

        triples.append(Triple(
            subject=file_uri_ref,
            predicate=predicate,
            object=object,
        ))
