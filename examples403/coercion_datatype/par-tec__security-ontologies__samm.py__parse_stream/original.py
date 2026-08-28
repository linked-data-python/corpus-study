# Extracted from par-tec/security-ontologies@d405f7555e : samm.py
# region: parse_stream (lines 81-99, stratum coercion_datatype)
# licence of the source repository: see meta.json
import yaml
from rdflib import DCAT, DCTERMS, SKOS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
NS_OS = Namespace("https://owaspsamm.org/model/")
BASEDIR = Path("external/samm-model")

def parse_stream(g):
    for f in (BASEDIR / "streams").glob("*.yml"):
        data = yaml.safe_load(f.read_text())
        id_ = data["id"]
        altLabel = f.name.replace(".yml", "")
        uri = URIRef(f"{NS_OS}{id_}")
        practice_uri = URIRef(NS_OS + data["practice"])
        g.add((uri, RDF.type, NS_OS.Stream))
        g.add((uri, RDFS.label, Literal(data["name"])))
        g.add((uri, SKOS.altLabel, Literal(altLabel)))
        g.add((uri, DCTERMS.identifier, Literal(id_)))
        g.add((uri, DCTERMS.description, Literal(data["description"])))
        g.add((uri, NS_OS.hasOrder, Literal(data["order"])))
        g.add((uri, NS_OS.hasLetter, Literal(data["letter"])))
        g.add((uri, NS_OS.hasPractice, practice_uri))

        # Relation to practice
        if practice := g.value(practice_uri, SKOS.altLabel):
            g.add((uri, NS_OS.practice, practice))
