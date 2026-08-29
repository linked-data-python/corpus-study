# Extracted from vital-ai/vital-graph@7fb3616c2d : test_scripts/archive/test_wordnet_loading.py
# region: WordNetDataLoader._convert_string_to_rdflib_term (lines 335-370, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, BNode

def _convert_string_to_rdflib_term(self, term_str: str):
    """Convert string representation to appropriate RDFLib term (matches working test script)."""
    term_str = term_str.strip()

    if term_str.startswith('<') and term_str.endswith('>'):
        # URI reference
        return URIRef(term_str[1:-1])  # Remove < >
    elif term_str.startswith('_:'):
        # Blank node
        return BNode(term_str[2:])  # Remove _:
    elif term_str.startswith('"'):
        # Literal - handle various forms
        if term_str.endswith('"'):
            # Simple literal
            return Literal(term_str[1:-1])  # Remove quotes
        else:
            # Literal with language tag or datatype
            if '"@' in term_str:
                # Language tag
                literal_part, lang_part = term_str.rsplit('"@', 1)
                literal_value = literal_part[1:]  # Remove opening quote
                return Literal(literal_value, lang=lang_part)
            elif '"^^' in term_str:
                # Datatype
                literal_part, datatype_part = term_str.rsplit('"^^', 1)
                literal_value = literal_part[1:]  # Remove opening quote
                if datatype_part.startswith('<') and datatype_part.endswith('>'):
                    datatype = URIRef(datatype_part[1:-1])
                else:
                    datatype = URIRef(datatype_part)
                return Literal(literal_value, datatype=datatype)
            else:
                return Literal(term_str[1:])  # Fallback
    else:
        # Assume URI if not quoted or blank node
        return URIRef(term_str)
