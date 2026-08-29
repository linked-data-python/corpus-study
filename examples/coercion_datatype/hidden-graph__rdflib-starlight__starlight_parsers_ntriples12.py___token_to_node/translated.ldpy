# Extracted from hidden-graph/rdflib-starlight@b7973da2b5 : starlight/parsers/ntriples12.py
# region: _token_to_node (lines 138-184, stratum coercion_datatype)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Literal
from starlight.model.triple import TripleTerm
from starlight.model.encoding import encode_dirlang_datatype

def _token_to_node(token: str):
    """Convert an N-Triples 1.2 token string to an rdflib node or TripleTerm."""
    token = token.strip()

    # Triple term
    if token.startswith('<<(') and token.endswith(')>>'):
        inner = token[3:-3].strip()
        tok_s, i = _consume_nt_term(inner, 0)
        tok_p, i = _consume_nt_term(inner, i)
        tok_o, _ = _consume_nt_term(inner, i)
        if tok_s is None or tok_p is None or tok_o is None:
            raise ValueError(f"Triple term must have exactly 3 components: {token!r}")
        return TripleTerm(_token_to_node(tok_s), _token_to_node(tok_p), _token_to_node(tok_o))

    # IRI
    if token.startswith('<') and token.endswith('>'):
        return URIRef(_unescape_nt(token[1:-1]))

    # Blank node
    if token.startswith('_:'):
        return BNode(token[2:])

    # Literal
    if token.startswith('"'):
        close = token.index('"', 1)
        while close > 0 and token[close - 1] == '\\':
            close = token.index('"', close + 1)
        value = _unescape_nt(token[1:close])
        suffix = token[close + 1:]
        if suffix.startswith('@'):
            lang_dir = suffix[1:]
            if '--' in lang_dir:
                # RDF 1.2 "text"@lang--dir (rdf:dirLangString) — see
                # starlight.parsers.turtle_parser._to_node for the same encoding.
                language, _, direction = lang_dir.rpartition('--')
                direction = direction.lower()
                if direction not in ('ltr', 'rtl'):
                    raise ValueError(
                        f'RDF 1.2: base direction must be "ltr" or "rtl", got {direction!r} in @{lang_dir}'
                    )
                return Literal(value, datatype=encode_dirlang_datatype(language.lower(), direction))
            return Literal(value, lang=lang_dir)
        if suffix.startswith('^^<') and suffix.endswith('>'):
            return Literal(value, datatype=URIRef(_unescape_nt(suffix[3:-1])))
        return Literal(value)

    raise ValueError(f"Unknown N-Triples 1.2 term: {token!r}")
