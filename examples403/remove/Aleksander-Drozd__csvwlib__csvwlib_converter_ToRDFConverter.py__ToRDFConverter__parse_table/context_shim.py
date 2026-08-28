# Context shim (see meta.json): the part of csvwlib/converter/ToRDFConverter.py
# that surrounds the region, transcribed from
# Aleksander-Drozd/csvwlib@6359de9b32 so that the region executes outside the
# package.  Identical bindings for both representations.
#
# Why a transcription and not the package itself: importing csvwlib pulls in
# csvwlib.utils.metadata, which needs the third-party `language_tags`
# distribution; it is not in the study venv and the venv is pinned.
#
# What is reproduced verbatim: the constructor, and the four collaborators the
# region calls -- _add_file_metadata, _parse_generic_row, _parse_row,
# _parse_row_data and parse_virtual_columns -- together with the two helper
# functions they reach on the fixtures used by driver.py
# (JSONLDUtils.language and CommonProperties.is_common_property).
#
# What is NOT reproduced: the per-cell branch of _parse_row_data and the
# virtual-column branch of parse_virtual_columns, which pull in six more
# csvwlib utility modules.  The fixtures give every row an empty `cells`
# mapping and declare no virtual column, so neither branch is entered; the
# stand-ins below raise rather than answer, so a future fixture that did enter
# them would fail loudly instead of diverging silently.
#
# Also omitted: RDFGraphUtils.add_default_bindings / add_bindings_from_metadata,
# called by the real constructor.  They only bind prefixes on the graph, which
# changes serialisation and not triples, and the oracle here is isomorphism.
from rdflib import Graph, Literal, BNode, Namespace, RDF, URIRef
from rdflib.namespace import XSD

CSVW = Namespace('http://www.w3.org/ns/csvw#')

# csvwlib/utils/rdf/CSVW.py
CONST_STANDARD_MODE = 'standard'
CONST_MINIMAL_MODE = 'minimal'


class JSONLDUtils:
    """csvwlib/utils/json/JSONLDUtils.py (the two methods reached)."""

    @staticmethod
    def language(context, metadata={}):
        language = JSONLDUtils.language_in_context(context)
        if language is not None:
            return language
        for key, value in metadata.items():
            if key == 'lang':
                return value

    @staticmethod
    def language_in_context(context):
        if type(context) is str:
            return None
        if type(context) is list:
            for value in context:
                if type(value) is dict and '@language' in value:
                    return value['@language']
        if type(context) is dict:
            return context.get('@language')


class CommonProperties:
    """csvwlib/utils/json/CommonProperties.py (the method reached)."""

    @staticmethod
    def is_common_property(prop):
        return ':' in prop and '://' not in prop

    @staticmethod
    def property_to_triples(entry, subject, language):
        raise NotImplementedError(
            "not reached by driver.py's fixtures: no metadata key is a common "
            "property; see the shim header")


class PropertyUrlUtils:
    """csvwlib/utils/url/PropertyUrlUtils.py -- not reached, see header."""

    @staticmethod
    def create_namespace(property_url, domain_url=''):
        raise NotImplementedError(
            "not reached by driver.py's fixtures: every row has empty cells; "
            "see the shim header")


class ToRDFConverter:

    def __init__(self, atdm, metadata):
        super().__init__()
        self.graph = Graph()
        self.metadata = metadata
        self.atdm = atdm
        self.mode = CONST_STANDARD_MODE

    def _add_file_metadata(self, metadata, node):
        language = JSONLDUtils.language(self.metadata['@context'])
        for key, value in metadata.items():
            if CommonProperties.is_common_property(key) or key == 'notes':
                triples = CommonProperties.property_to_triples((key, metadata[key]), node, language)
                self.graph.addN(triple + (self.graph,) for triple in triples)

    def _parse_generic_row(self, atdm_row, table_node, metadata, property_url, row_node, atdm_table):
        self.graph.add((table_node, CSVW.row, row_node))
        self.graph.add((row_node, RDF.type, CSVW.Row))
        self.graph.add((row_node, CSVW.rownum, Literal(atdm_row['number'], datatype=XSD.integer)))
        self.graph.add((row_node, CSVW.url, URIRef(atdm_row['@id'])))
        if 'rowTitles' in metadata['tableSchema']:
            col_names = metadata['tableSchema']['rowTitles']
            for col_name in col_names:
                col_value = atdm_row['cells'][col_name][0]
                self.graph.add((row_node, CSVW.title, Literal(col_value)))
        values_node = BNode()
        self._parse_row(atdm_row, values_node, row_node, metadata, property_url, atdm_table)

    def _parse_row(self, atdm_row, values_node, row_node, metadata, property_url, atdm_Table):
        if not all(map(lambda column: 'aboutUrl' in column, metadata['tableSchema']['columns'])):
            self.graph.add((row_node, CSVW.describes, values_node))
        self._parse_row_data(atdm_row, values_node, metadata, property_url, row_node, atdm_Table)

    def _parse_row_data(self, atdm_row, subject, table_metadata, property_url, row_node, atdm_table):
        top_level_property_url = property_url
        atdm_columns = atdm_table['columns']
        for index, entry in enumerate(atdm_row['cells'].items()):
            raise NotImplementedError(
                "not reached by driver.py's fixtures: every row has empty "
                "cells; see the shim header")

    def parse_virtual_columns(self, row_node, atdm_row, table_metadata):
        for virtual_column in table_metadata['tableSchema']['columns']:
            if 'virtual' not in virtual_column or virtual_column['virtual'] is False:
                continue
            raise NotImplementedError(
                "not reached by driver.py's fixtures: no column is virtual; "
                "see the shim header")
