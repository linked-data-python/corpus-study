# Extracted from par-tec/security-ontologies@d405f7555e : samm.py
# region: parse_activity (lines 171-246, stratum add_in_loop)
# licence of the source repository: see meta.json
import yaml
from rdflib import DCAT, DCTERMS, SKOS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
NS_OS = Namespace("https://owaspsamm.org/model/")
BASEDIR = Path("external/samm-model")

def parse_activity(g):
    # links to Maturity Level
    #
    """
        ---
    # ===========================================================
    # OWASP SAMM Activity Description
    # ===========================================================
    stream: 253b012094cf4e0988e08fd22609227d
    level: a11b78917dec4cfdad983cf6d1d17b61
    id: 27bb61f3c6344359b021caeaef5ab07e
    title: Adhere to basic security principles
    benefit: Sets of security basic principles available to product teams
    shortDescription: Teams are trained on the use of basic security principles during
      design
    longDescription: |
      During design, technical staff on the product team use a short checklist
       of security principles. Typically, security principles include defense in depth,
       securing the weakest link, use of secure defaults, simplicity in design of security functionality,
        secure failure, balance of security and usability, running with least privilege,
         avoidance of security by obscurity, etc.

      For perimeter interfaces, the team considers each principle in the context of
       the overall system and identify features that can be added to bolster security
       at each such interface. Limit these such that they only take a small amount of
       extra effort beyond the normal implementation cost of functional requirements.
        Note anything larger, and schedule it for future releases.

      Train each product team with security awareness before this process,
      and incorporate more security-savvy staff to aid in making design decisions.

    #The output of this particular activity
    results:

    #The different metrics that can be used to measure the success of the activity
    metrics:

    #A description of the costs required to implement the activity
    costs:
    #The (standard) roles involved in the implementation of this activity
    personnel:

    #Internal notes that might help the author
    notes:

    #References to other activities that are prerequesites to implement this one.
    relatedActivities:
    #Type Classification of the Document
    type: Activity"""
    for f in (BASEDIR / "activities").glob("*.yml"):
        data = yaml.safe_load(f.read_text())
        id_ = data["id"]

        uri = URIRef(f"{NS_OS}{id_}")
        practicelevel_uri = URIRef(NS_OS + data["level"])
        stream_uri = URIRef(NS_OS + data["stream"])
        g.add((uri, RDF.type, NS_OS.Activity))
        g.add((uri, RDFS.label, Literal(data["title"])))
        g.add((uri, SKOS.altLabel, Literal(f.name.replace(".yml", ""))))
        g.add((uri, DCTERMS.identifier, Literal(id_)))
        g.add((uri, DCTERMS.description, Literal(data["longDescription"])))
        g.add((uri, RDFS.comment, Literal(data["shortDescription"])))
        g.add((uri, NS_OS.hasStream, stream_uri))
        g.add((uri, NS_OS.hasPracticeLevel, practicelevel_uri))
        g.add((uri, NS_OS.benefit, Literal(data["benefit"])))

        # Relation solver.
        if stream_name := g.value(stream_uri, NS_OS.hasLetter):
            stream_suffix = f"stream-{stream_name}".lower()
            if practice_uri := g.value(stream_uri, NS_OS.hasPractice):
                practice_url = g.value(practice_uri, OWL.sameAs)
                _, _, maturity, _ = f.name.replace(".yml", "").split("-")
                alias_uri = URIRef(practice_url + f"/{stream_suffix}#{maturity}")
                g.add((uri, OWL.sameAs, alias_uri))
                g.add((alias_uri, RDF.type, NS_OS.Activity))
                g.add((alias_uri, OWL.sameAs, uri))
