# Extracted from trickle-labs/riverbank@38559ddfe9 : src/riverbank/postprocessors/shacl_validator.py
# region: ShaclValidator._fetch_graph (lines 210-261, stratum add_in_loop)
# licence of the source repository: see meta.json
from typing import Any
logger = logging.getLogger(__name__)

    def _fetch_graph(
        self,
        conn: Any,
        named_graph: str,
        rdflib: Any,
    ) -> Any | None:
        """Fetch all triples from *named_graph* and build an rdflib Graph."""
        from riverbank.catalog.graph import sparql_query  # noqa: PLC0415

        sparql = f"""\
SELECT ?s ?p ?o WHERE {{
  GRAPH <{named_graph}> {{
    ?s ?p ?o .
  }}
}}
LIMIT 10000
"""
        try:
            rows = sparql_query(conn, sparql)
        except Exception as exc:  # noqa: BLE001
            logger.warning("shacl_validator: could not fetch triples — %s", exc)
            return None

        g = rdflib.Graph()
        for row in rows:
            s_raw = str(row.get("s", ""))
            p_raw = str(row.get("p", ""))
            o_raw = str(row.get("o", ""))
            if not (s_raw and p_raw and o_raw):
                continue
            try:
                s = rdflib.URIRef(s_raw) if s_raw.startswith("http") else rdflib.BNode(s_raw)
                p = rdflib.URIRef(p_raw)
                # Try to distinguish literals from URIs
                if o_raw.startswith("http") or o_raw.startswith("_:"):
                    o: Any = rdflib.URIRef(o_raw)
                else:
                    # Try to detect datatype annotations e.g. "1.0"^^xsd:decimal
                    if "^^" in o_raw:
                        val, dtype = o_raw.rsplit("^^", 1)
                        val = val.strip('"')
                        o = rdflib.Literal(val, datatype=rdflib.URIRef(dtype))
                    elif o_raw.startswith('"') or not o_raw.startswith("<"):
                        o = rdflib.Literal(o_raw.strip('"'))
                    else:
                        o = rdflib.URIRef(o_raw.strip("<>"))
                g.add((s, p, o))
            except Exception:  # noqa: BLE001
                continue

        logger.debug("shacl_validator: loaded %d triples from <%s>", len(g), named_graph)
        return g
