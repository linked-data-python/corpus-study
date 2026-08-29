# Extracted from par-tec/security-ontologies@d405f7555e : samm.py
# region: parse_maturity (lines 57-72, stratum add_in_loop)
# licence of the source repository: see meta.json
import yaml
from rdflib import DCAT, DCTERMS, SKOS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
NS_OS = Namespace("https://owaspsamm.org/model/")
BASEDIR = Path("external/samm-model")

def parse_maturity(g):
    for f in (BASEDIR / "maturity_levels").glob("*.yml"):
        data = yaml.safe_load(f.read_text())
        id_ = data["id"]
        uri = URIRef(f"{NS_OS}{id_}")
        g.add((uri, RDF.type, NS_OS.MaturityLevel))
        g.add((uri, RDFS.label, Literal(data["number"])))
        g.add((uri, DCTERMS.identifier, Literal(id_)))
        g.add((uri, SKOS.altLabel, Literal(data["number"])))
        g.add((uri, DCTERMS.description, Literal(data["description"])))

        # Relation
        hr_uri = URIRef(f"{NS_OS}maturity/{data['number']}")
        g.add((hr_uri, RDF.type, NS_OS.MaturityLevel))
        g.add((hr_uri, DCTERMS.identifier, Literal(id_)))
        g.add((hr_uri, OWL.sameAs, uri))
