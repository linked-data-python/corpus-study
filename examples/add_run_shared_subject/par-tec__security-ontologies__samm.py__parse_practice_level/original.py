# Extracted from par-tec/security-ontologies@d405f7555e : samm.py
# region: parse_practice_level (lines 108-131, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import yaml
from rdflib import DCAT, DCTERMS, SKOS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
NS_OS = Namespace("https://owaspsamm.org/model/")
BASEDIR = Path("external/samm-model")

def parse_practice_level(g):
    # links to practice, maturitylevel
    #
    for f in (BASEDIR / "practice_levels").glob("*.yml"):
        data = yaml.safe_load(f.read_text())
        id_ = data["id"]
        name = f.name.replace(".yml", "")
        uri = URIRef(f"{NS_OS}{id_}")
        g.add((uri, RDF.type, NS_OS.PracticeLevel))
        g.add((uri, RDFS.label, Literal(name)))
        g.add((uri, SKOS.altLabel, Literal(name)))
        g.add((uri, DCTERMS.identifier, Literal(id_)))
        g.add((uri, DCTERMS.description, Literal(data["objective"])))

        maturitylevel_uri = URIRef(NS_OS + data["maturitylevel"])
        practice_uri = URIRef(NS_OS + data["practice"])
        g.add((uri, NS_OS.hasMaturityLevel, maturitylevel_uri))
        g.add((uri, NS_OS.hasPractice, practice_uri))

        if maturitylevel := g.value(maturitylevel_uri, SKOS.altLabel):
            g.add((uri, NS_OS.maturitylevel, maturitylevel))

        if practice := g.value(practice_uri, SKOS.altLabel):
            g.add((uri, NS_OS.practice, practice))
