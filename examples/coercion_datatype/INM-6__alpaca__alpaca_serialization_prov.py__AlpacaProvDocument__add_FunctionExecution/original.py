# Extracted from INM-6/alpaca@2b8dd34fc6 : alpaca/serialization/prov.py
# region: AlpacaProvDocument._add_FunctionExecution (lines 162-193, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, BNode, Literal
from rdflib.namespace import RDF, PROV, XSD
from alpaca.ontology import ALPACA
from alpaca.serialization.identifiers import (data_object_identifier,
                                              file_identifier,
                                              function_identifier,
                                              script_identifier,
                                              execution_identifier,
                                              _get_function_name)
from alpaca.serialization.converters import _ensure_type

def _add_FunctionExecution(self, script_info, session_id, execution_id,
                           function_info, params, execution_order,
                           code_statement, start, end, function,
                           ontology_info=None):
    # Adds a FunctionExecution record from the Alpaca PROV model
    uri = URIRef(execution_identifier(
        script_info, function_info, session_id, execution_id,
        self._authority))
    self.graph.add((uri, RDF.type, ALPACA.FunctionExecution))

    if ontology_info:
        self._add_ontology_information(uri, ontology_info, 'function')

    self.graph.add((uri, PROV.startedAtTime,
                    Literal(start, datatype=XSD.dateTime)))
    self.graph.add((uri, PROV.endedAtTime,
                    Literal(end, datatype=XSD.dateTime)))
    self.graph.add((uri, ALPACA.codeStatement, Literal(code_statement)))
    self.graph.add((uri, ALPACA.executionOrder,
                    Literal(execution_order, datatype=XSD.integer)))
    self.graph.add((uri, ALPACA.usedFunction, function))

    for name, value in params.items():
        value = _ensure_type(value)
        parameter_node = _add_name_value_pair(self.graph, uri,
                                              ALPACA.hasParameter,
                                              name, value)
        if ontology_info:
            self._add_ontology_information(parameter_node,
                                           ontology_info, 'arguments',
                                           name)
    return uri
