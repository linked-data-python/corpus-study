# Extracted from semanticarts/ontology-toolkit@99a1a00917 : onto_tool/bundle.py
# region: __bundle_transform_sparql__ (lines 172-202, stratum bind_initbindings)
# licence of the source repository: see meta.json
from os.path import basename, isdir, isfile, join, splitext
from rdflib import Graph, Literal
from rdflib.namespace import OWL, RDFS, SKOS, XSD, Namespace
from rdflib.util import guess_format
# Context shim: __bundle_file_list, parse_rdf, replace_patterns_in_file and
# __parse_update_query__ live elsewhere in bundle.py/utils.py; restoring the
# bindings so the region executes standalone (see shim.py).
from shim import parse_rdf, __bundle_file_list, __parse_update_query__, \
                  replace_patterns_in_file

def __bundle_transform_sparql__(action, tool, variables):
    query = tool['query'].format(**variables)
    if isfile(query):
        with open(query, 'r', encoding='utf-8') as qfile:
            query_text = qfile.read()
    else:
        query_text = query

    parsed_query = __parse_update_query__(query_text)

    for in_out in __bundle_file_list(action, variables):
        g = Graph()
        onto_file = in_out['inputFile']
        rdf_format = guess_format(onto_file)
        parse_rdf(g, onto_file, rdf_format=rdf_format)

        g.update(
            parsed_query,
            initNs={'xsd': XSD, 'owl': OWL, 'rdfs': RDFS, 'skos': SKOS})

        if 'format' in tool:
            rdf_format = 'pretty-xml' if action['format'] == 'xml' else action['format']

        g.serialize(destination=in_out['outputFile'],
                    format=rdf_format, encoding='utf-8')

        if 'replace' in action:
            replace_patterns_in_file(in_out['outputFile'],
                                     action['replace']['from'].format(
                                         **variables),
                                     action['replace']['to'].format(**variables))
