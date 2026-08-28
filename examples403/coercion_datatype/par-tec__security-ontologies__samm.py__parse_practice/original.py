# Extracted from par-tec/security-ontologies@d405f7555e : samm.py
# region: parse_practice (lines 140-162, stratum coercion_datatype)
# licence of the source repository: see meta.json
import yaml
from rdflib import DCAT, DCTERMS, SKOS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
NS_OS = Namespace("https://owaspsamm.org/model/")
BASEDIR = Path("external/samm-model")

def parse_practice(g):
    # links to Maturity Level
    #
    for f in (BASEDIR / "security_practices").glob("*.yml"):
        data = yaml.safe_load(f.read_text())
        id_ = data["id"]

        uri = URIRef(f"{NS_OS}{id_}")
        function_uri = URIRef(NS_OS + data["function"])
        practice_uri = data["name"].lower().replace("&", "and").replace(" ", "-")
        g.add((uri, RDF.type, NS_OS.Practice))
        g.add((uri, RDFS.label, Literal(data["name"])))
        g.add((uri, SKOS.altLabel, Literal(data["shortName"])))
        g.add((uri, DCTERMS.identifier, Literal(id_)))
        g.add((uri, DCTERMS.description, Literal(data["longDescription"])))
        g.add((uri, RDFS.comment, Literal(data["shortDescription"])))
        g.add((uri, NS_OS.hasOrder, Literal(data["order"])))
        g.add((uri, NS_OS.hasFunction, function_uri))

        # Relation solver.
        if function_name := g.value(function_uri, SKOS.altLabel):
            aliasURI = URIRef(f"{NS_OS}{function_name}/{practice_uri}")
            g.add((uri, OWL.sameAs, aliasURI))
