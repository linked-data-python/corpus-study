# Extracted from INM-6/alpaca@2b8dd34fc6 : alpaca/serialization/prov.py
# region: AlpacaProvDocument._add_function_execution (lines 309-398, stratum trav_existence)
# licence of the source repository: see meta.json
from itertools import product, chain
from rdflib.namespace import RDF, PROV, XSD
from alpaca.serialization.identifiers import (data_object_identifier,
                                              file_identifier,
                                              function_identifier,
                                              script_identifier,
                                              execution_identifier,
                                              _get_function_name)
from alpaca.alpaca_types import DataObject, File, Container
from alpaca.ontology.annotation import _OntologyInformation, ONTOLOGY_INFORMATION

def _add_function_execution(self, execution, script_agent, script_info,
                            session_id):
    # Add one `FunctionExecution` record to the file, and generate all the
    # provenance semantic relationships

    def _is_membership(function_info):
        name = function_info.name
        return name in ("attribute", "subscript")

    function_info = execution.function
    if _is_membership(function_info):
        # attributes and subscripting operations
        container = execution.input[0]
        child = execution.output[0]
        container_entity = self._create_entity(container)
        if PROV.wasAttributedTo not in \
                self.graph.predicates(container_entity, script_agent):
            self._wasAttributedTo(container_entity, script_agent)
        child_entity = self._create_entity(child)
        self._add_membership(container_entity, child_entity,
                             execution.params)
    else:
        # This is a function execution. Add Function activity
        cur_function = self._add_Function(function_info)

        # ID to identify ontology annotations
        info_id = _get_function_name(function_info)
        ontology_info = ONTOLOGY_INFORMATION.get(info_id)

        # Get the FunctionExecution node with function parameters and
        # other provenance info
        cur_activity = self._add_FunctionExecution(
            script_info=script_info, session_id=session_id,
            execution_id=execution.execution_id,
            function_info=function_info, params=execution.params,
            execution_order=execution.order,
            code_statement=execution.code_statement,
            start=execution.time_stamp_start,
            end=execution.time_stamp_end,
            function=cur_function, ontology_info=ontology_info
        )

        # Add all the inputs as entities, and create a `used` association
        # with the activity. URNs differ when the input is a file or
        # Python object.
        input_entities = []
        for key, value in execution.input.items():
            cur_entities = []
            has_input_uri = ontology_info and \
                            bool(ontology_info.get_uri('arguments', key))

            if isinstance(value, Container):
                # If this is a Container, several objects are inside.
                for element in value.elements:
                    cur_entities.append(self._create_entity(element))
            else:
                cur_entities.append(self._create_entity(value))

            input_entities.extend(cur_entities)

            for cur_entity in cur_entities:
                self._used(activity=cur_activity, entity=cur_entity)
                self._wasAttributedTo(entity=cur_entity,
                                      agent=script_agent)
                if has_input_uri:
                    self._add_ontology_information(cur_entity,
                                                   ontology_info,
                                                   'arguments', key)

        # Add all the outputs as entities, and create the `wasGenerated`
        # relationship.
        output_entities = []
        for key, value in execution.output.items():
            cur_entity = self._create_entity(value)
            output_entities.append(cur_entity)
            self._wasGeneratedBy(entity=cur_entity, activity=cur_activity)
            self._wasAttributedTo(entity=cur_entity, agent=script_agent)
            if ontology_info:
                self._add_ontology_information(cur_entity, ontology_info,
                                               'returns', element=key)

        # Iterate over the input/output pairs to add the `wasDerived`
        # relationship
        for input_entity, output_entity in \
                product(input_entities, output_entities):
            self._wasDerivedFrom(used_entity=input_entity,
                                 generated_entity=output_entity)

        # Associate the activity to the script
        self._wasAssociatedWith(activity=cur_activity, agent=script_agent)
