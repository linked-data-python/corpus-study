# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/services/triple_store/adaptors/secondary/Oxigraph.py
# region: Oxigraph.query (lines 429-510, stratum coercion_datatype)
# licence of the source repository: see meta.json
#
# The region as extracted is a bare `if/elif/else` block with a `return` in
# each branch: it is not runnable outside the enclosing method. Restoring the
# binding here (rdfeval.harness.run_pair needs a callable) means wrapping it
# in a function taking `response` and `content_type` as parameters -- exactly
# the two names the original method reads that the extracted lines do not
# define themselves. No other change.
from rdflib import BNode, Graph, URIRef


def query(response, content_type):
    if "sparql-results" in content_type:
        # SELECT or ASK query - parse JSON results
        import json

        result_data = json.loads(response.text)

        # Create a result wrapper that's compatible with RDFLib's ResultRow
        from rdflib.query import ResultRow
        from rdflib.term import Literal, Variable

        # Extract variables
        vars = result_data.get("head", {}).get("vars", [])
        bindings = result_data.get("results", {}).get("bindings", [])

        # Convert variable names to Variable objects
        var_objects = [Variable(var) for var in vars]

        def to_term(binding_info):
            value_str = binding_info["value"]
            binding_type = binding_info.get("type", "literal")
            datatype = binding_info.get("datatype")
            # Convert to appropriate RDFLib term
            if binding_type == "uri":
                return URIRef(value_str)
            if binding_type == "bnode":
                return BNode(value_str)
            if datatype in [
                "http://www.w3.org/2001/XMLSchema#integer",
                "http://www.w3.org/2001/XMLSchema#long",
            ]:
                # Handle numeric datatypes
                try:
                    return Literal(int(value_str), datatype=URIRef(datatype))
                except ValueError:
                    pass
            if datatype:
                return Literal(value_str, datatype=URIRef(datatype))
            return Literal(value_str, lang=binding_info.get("xml:lang") or None)

        # Convert bindings to result rows
        results = [
            ResultRow(
                {Variable(var): to_term(binding[var]) for var in vars if var in binding},
                var_objects,
            )
            for binding in bindings
        ]

        # Return an iterable result
        return iter(results)  # type: ignore
    elif "n-triples" in content_type or "turtle" in content_type:
        # CONSTRUCT or DESCRIBE query
        format_type = "nt" if "n-triples" in content_type else "turtle"
        return Graph().parse(data=response.text, format=format_type)  # type: ignore
    raise ValueError(f"Unexpected content type: {content_type}")
