# Extracted from INM-6/alpaca@2b8dd34fc6 : alpaca/serialization/prov.py
# region: AlpacaProvDocument._add_annotations_for_container_outputs (lines 400-461, stratum trav_one_step)
# licence of the source repository: see meta.json
from itertools import product, chain
from rdflib.namespace import RDF, PROV, XSD
from alpaca.ontology.annotation import _OntologyInformation, ONTOLOGY_INFORMATION

def _add_annotations_for_container_outputs(self):
    # For functions that the Provenance decorator identified elements
    # inside returned containers, the elements linked by `prov:hasMember`
    # functions need to be annotated. The list of functions is already
    # stored in a search list. Iterate over the nodes of the function
    # and annotate the correct level of membership

    for info_id, levels in self._container_output_functions.items():

        # Initialize a container to store the URIs of elements of each
        # output level starting from the function. Since the capture can
        # ignore root levels, and to avoid recursion, we will map
        # container entities up to the maximum possible level taken from
        # the 'returns' annotations. Later, we take the annotations
        # starting from the deepest level.

        int_levels = list(map(lambda x: len(x), levels))
        max_level = max(int_levels)
        elements_by_level = {level: [] for level in range(max_level)}

        # Fetch information on the function, to identify nodes in the graph
        ontology_info = ONTOLOGY_INFORMATION[info_id]
        function_type = ontology_info.get_uri('function')
        executions = self.graph.subjects(RDF.type, function_type)

        # For every execution, get the output nodes
        # This is the first level
        for execution in executions:
            elements_by_level[0].extend(
                self.graph.subjects(PROV.wasGeneratedBy, execution))

        # Traverse the remaining levels
        for level in range(1, max_level):
            for element in chain(elements_by_level[level-1]):
                members = self.graph.objects(element, PROV.hadMember)
                elements_by_level[level].extend(members)

        # Go from the deepest annotation level, annotating the deepest
        # node level with elements
        level_depth = max_level - 1
        level_str = '*' * max_level
        obj_uri = ontology_info.get_uri('returns', level_str)

        while level_depth >= 0:
            if obj_uri:
                has_elements = False
                for element in chain(elements_by_level[level_depth]):
                    has_elements = True
                    self.graph.add((element, RDF.type, obj_uri))
            else:
                # No annotation requested for this level
                # Consider the level traversed
                has_elements = True

            if has_elements:
                # Fetch annotation information for the parent level
                level_str = '*' * (len(level_str) - 1)
                obj_uri = ontology_info.get_uri('returns', level_str)

            # If no element found, keep the annotation level, but
            # try to annotate the elements of an upper node level
            level_depth -= 1
