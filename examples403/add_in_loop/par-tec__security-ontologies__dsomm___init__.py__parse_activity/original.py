# Extracted from par-tec/security-ontologies@d405f7555e : dsomm/__init__.py
# region: parse_activity (lines 73-137, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import DCAT, DCTERMS, SKOS, Graph, Literal, Namespace, URIRef
from rdflib.namespace import OWL, RDF, RDFS
NS_DSOMM = Namespace("https://owasp.org/www-project-devsecops-maturity-model/")
NS_D3F = Namespace("http://d3fend.mitre.org/ontologies/d3fend.owl#")

def parse_activity(g, activity_name, activity, subdimension_uri):
    """
    description: |-
      While building and testing artifacts, third party systems, application frameworks
      and 3rd party libraries are used. These might be malicious as a result of
      vulnerable libraries or because they are altered during the delivery phase.
    risk: |-
      While building and testing artifacts, third party systems, application frameworks
      and 3rd party libraries are used. These might be malicious as a result of
      vulnerable libraries or because they are altered during the delivery phase.
    measure: Each step during within the build and testing phase is performed in
      a separate virtual environments, which is destroyed afterward.
    meta:
      implementationGuide: Depending on your environment, usage of virtual machines
        or container technology is a good way. After the build, the filesystem should
        not be used again in other builds.
    difficultyOfImplementation:
      knowledge: 2
      time: 2
      resources: 2
    usefulness: 2
    level: 2
    implementation:
    - name: CI/CD tools
      tags:
      - ci-cd
      url: https://martinfowler.com/articles/continuousIntegration.html
      description: CI/CD tools such as jenkins, gitlab-ci or github-actions
    - name: Container technologies and orchestration like Docker, Kubernetes
      tags: []
    references:
      samm2:
      - I-SB-2-A
      iso27001-2017:
      - 14.2.6
    isImplemented: true
    evidence: ""
    comments: ""
    assessment: ""

    """
    activity_uri = URIRef(NS_DSOMM + activity_name.title().replace(" ", ""))
    g.add((activity_uri, RDF.type, NS_DSOMM.Activity))
    g.add((activity_uri, RDFS.label, Literal(activity_name)))
    g.add((activity_uri, NS_DSOMM.hasSubdimension, subdimension_uri))

    g.add((activity_uri, RDFS.comment, Literal(activity.get("description", ""))))
    g.add((activity_uri, NS_DSOMM.Measure, Literal(activity.get("measure", ""))))
    g.add((activity_uri, NS_DSOMM.assessment, Literal(activity.get("assessment", ""))))
    for i in activity.get("implementation", []):
        if "url" not in i:
            continue
        implementation_url = URIRef(i["url"].strip("/"))
        g.add((activity_uri, NS_DSOMM.hasImplementation, implementation_url))
        g.add((implementation_url, RDF.type, NS_DSOMM.Implementation))
        g.add((implementation_url, RDFS.label, Literal(i["name"])))
        g.add((implementation_url, RDFS.comment, Literal(i.get("description", ""))))
        for t in i.get("tags", []):
            if t.startswith("d3f:"):
                g.add((implementation_url, NS_DSOMM.hasTag, URIRef(NS_D3F + t[4:])))
                continue
            g.add((implementation_url, NS_DSOMM.hasTag, Literal(t)))

    for reference in parse_references(activity.get("references", {})):
        g.add((activity_uri, NS_DSOMM.hasReference, reference))
