# Extracted from pyiron/semantikon@cfd1d3ffe5 : semantikon/ontology.py
# region: _function_to_graph (lines 429-521, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import OWL, RDF, RDFS, BNode, Graph, Literal, Namespace, URIRef
BASE: Namespace = Namespace("http://pyiron.org/ontology/")

def _function_to_graph(
    f_node: URIRef,
    data: dict,
    input_args: list[dict] | tuple[dict, ...],
    output_args: list[dict] | tuple[dict, ...],
    uri: URIRef | None = None,
) -> Graph:
    """
    Converts a function's metadata into an RDF graph representation.

    Args:
        f_node (URIRef): The URI reference for the function node.
        data (dict): A dictionary containing metadata about the function.
                     Expected keys:
                     - "qualname" (str): The qualified name of the function.
                     - "docstring" (str, optional): The docstring of the function.
        input_args (list[dict]): A list of dictionaries representing input arguments.
        output_args (list[dict]): A list of dictionaries representing output arguments.
        uri (URIRef | None, optional): The URI of the function, if available.

    Returns:
        Graph: An RDF graph representing the function and its metadata.
    """
    g = _get_bound_graph()
    g.add((f_node, RDF.type, SNS.workflow_function))
    f_name = BASE[data["qualname"] + "_function_name"]
    g.add((f_name, RDF.type, SNS.function_name))
    g.add((f_name, SNS.has_value, Literal(data["qualname"])))
    g.add((f_node, SNS.denoted_by, f_name))
    g.add(
        (
            f_name,
            RDFS.label,
            Literal(f"Function name '{data['qualname']}'"),
        )
    )
    if data.get("docstring", "") != "":
        docstring = URIRef(f_node + "_docstring")
        g.add((docstring, RDF.type, SNS.textual_entity))
        g.add((docstring, SNS.has_value, Literal(data["docstring"])))
        g.add((docstring, SNS.is_about, f_node))
    if uri is not None:
        assert isinstance(uri, URIRef)
        instance_iri = URIRef(f"{f_node}_instance")
        g.add((f_node, SNS.is_about, instance_iri))
        g.add((instance_iri, RDF.type, uri))
    if data.get("hash", "") != "":
        hash_bnode = URIRef(f_node + "_hash")
        g.add((f_node, SNS.denoted_by, hash_bnode))
        g.add((hash_bnode, RDF.type, SNS.identifier))
        g.add((hash_bnode, SNS.has_value, Literal(data["hash"])))
        g.add((hash_bnode, RDFS.label, Literal(f"{data['qualname']}_hash")))
    if data.get("module", "") != "":
        module = BASE[data["module"].replace(".", "_")]
        g.add((f_node, SNS.denoted_by, module))
        g.add((module, RDF.type, SNS.import_path))
        g.add((module, SNS.has_value, Literal(data["module"])))
    for io, io_args in zip(["input", "output"], [input_args, output_args]):
        for ii, arg in enumerate(io_args):
            if "label" in arg:
                arg_name = arg["label"]
            elif "arg" in arg:
                arg_name = arg["arg"]
            else:
                arg_name = f"output_{ii}"
            arg_node = URIRef(f"{f_node}_{io}_{arg_name}")
            if io == "input":
                g.add((arg_node, RDF.type, SNS.input_specification))
            else:
                g.add((arg_node, RDF.type, SNS.output_specification))
            g.add((arg_node, SNS.local_identifier, Literal(arg_name)))
            g.add((f_node, SNS.has_part, arg_node))
            g.add(
                (arg_node, SNS.has_parameter_position, Literal(arg.get("position", ii)))
            )
            if "default" in arg:
                g.add(
                    (arg_node, SNS.has_default_literal_value, Literal(arg["default"]))
                )
            if "uri" in arg:
                assert isinstance(arg["uri"], URIRef)
                uri_node = BNode(str(arg_node) + "_uri")
                g.add((uri_node, RDF.type, OWL.Restriction))
                g.add((uri_node, OWL.onProperty, SNS.is_about))
                g.add((uri_node, OWL.allValuesFrom, arg["uri"]))
                g.add((arg_node, RDF.type, uri_node))
            if "restrictions" in arg:
                g += _restrictions_to_triples(
                    arg["restrictions"],
                    data_node=arg_node,
                    predicate=SNS.has_constraint,
                )
    return g
