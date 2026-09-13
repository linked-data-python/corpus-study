# Context shim (see meta.json): subset of onto_tool/bundle.py and
# onto_tool/utils.py from semanticarts/ontology-toolkit@99a1a00917, so the
# region executes outside the package.
# Identical bindings for both representations.
import sys
import logging
from os.path import isdir, isfile

from rdflib import Graph
from rdflib.plugins.parsers.notation3 import BadSyntax
from rdflib.util import guess_format


def parse_rdf(g: Graph, onto_file: str, rdf_format: str = None):
    """Import local RDF content into the graph, report parse error.

    Copied from onto_tool/utils.py, unchanged.
    """
    try:
        g.parse(onto_file, format=rdf_format if rdf_format is not None else guess_format(
            onto_file))
    except BadSyntax as se:
        text, why = (se._str.decode('utf-8'), se._why)
        if len(text) > 30:
            text = text[0:27] + '...'
        logging.error("Error parsing %s at %d: %s: %s",
                      onto_file, se.lines + 1, why, text)
        sys.exit(1)


def __bundle_file_list(action, variables, ignore_target=False):
    """Expand a source/target spec into inputFile/outputFile pairs.

    Copied from onto_tool/bundle.py, trimmed of the includes/excludes glob
    branch (not exercised by this region's fixture) but otherwise unchanged.
    """
    yield {
        'inputFile': action['source'].format(**variables),
        'outputFile': None if ignore_target else action['target'].format(**variables)
    }


def replace_patterns_in_file(file, from_pattern, to_string):
    """Replace regex pattern in file contents. Copied from bundle.py, unchanged."""
    import re
    with open(file, 'r') as f:
        replaced = re.compile(from_pattern).sub(to_string, f.read())
    with open(file, 'w') as f:
        f.write(replaced)


def __parse_update_query__(query_text):
    """Copied from onto_tool/bundle.py, unchanged.

    Parses the SPARQL UPDATE text into rdflib's internal algebra -- this is
    exactly why the update at the region's bind_initbindings site cannot be
    written as `s{ ... }`: the query text is not a literal known when the
    file is transpiled, it is read from a variable at run time (a tool
    config value, sometimes itself the content of an external file).
    """
    from rdflib.plugins.sparql.algebra import translateUpdate
    from rdflib.plugins.sparql.parser import parseUpdate
    parsed_query = translateUpdate(parseUpdate(query_text))
    return parsed_query
