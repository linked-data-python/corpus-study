# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/services/triple_store/adaptors/secondary/Oxigraph.py
# region: Oxigraph.query (lines 429-510, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, URIRef

if "sparql-results" in content_type:
    # SELECT or ASK query - parse JSON results
    import json

    result_data = json.loads(response.text)

    # Create a result wrapper that's compatible with RDFLib's ResultRow
    from rdflib.query import ResultRow
    from rdflib.term import BNode, Literal, URIRef, Variable

    # Extract variables
    vars = result_data.get("head", {}).get("vars", [])
    bindings = result_data.get("results", {}).get("bindings", [])

    # Convert variable names to Variable objects
    var_objects = [Variable(var) for var in vars]

    # Convert bindings to result rows
    results = []

    for binding in bindings:
        row_values = {}

        for var in vars:
            var_obj = Variable(var)

            if var in binding:
                binding_info = binding[var]
                value_str = binding_info["value"]
                binding_type = binding_info.get("type", "literal")

                # Convert to appropriate RDFLib term
                value: URIRef | BNode | Literal | None
                if binding_type == "uri":
                    value = URIRef(value_str)
                elif binding_type == "bnode":
                    value = BNode(value_str)
                else:  # literal
                    datatype = binding_info.get("datatype")
                    lang = binding_info.get("xml:lang")

                    if datatype:
                        # Handle numeric datatypes
                        if datatype in [
                            "http://www.w3.org/2001/XMLSchema#integer",
                            "http://www.w3.org/2001/XMLSchema#long",
                        ]:
                            try:
                                value = Literal(
                                    int(value_str), datatype=URIRef(datatype)
                                )
                            except ValueError:
                                value = Literal(
                                    value_str, datatype=URIRef(datatype)
                                )
                        else:
                            value = Literal(
                                value_str, datatype=URIRef(datatype)
                            )
                    elif lang:
                        value = Literal(value_str, lang=lang)
                    else:
                        value = Literal(value_str)

                row_values[var_obj] = value
            else:
                row_values[var_obj] = None  # type: ignore

        # Create a ResultRow compatible object
        row = ResultRow(row_values, var_objects)
        results.append(row)

    # Return an iterable result
    return iter(results)  # type: ignore
elif "n-triples" in content_type or "turtle" in content_type:
    # CONSTRUCT or DESCRIBE query
    graph = Graph()
    format_type = "nt" if "n-triples" in content_type else "turtle"
    graph.parse(data=response.text, format=format_type)
    return graph  # type: ignore
else:
    raise ValueError(f"Unexpected content type: {content_type}")
