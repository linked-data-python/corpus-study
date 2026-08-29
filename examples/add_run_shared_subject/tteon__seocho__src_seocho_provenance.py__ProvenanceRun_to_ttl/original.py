# Extracted from tteon/seocho@09f72a4569 : src/seocho/provenance.py
# region: ProvenanceRun.to_ttl (lines 82-121, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
_PROV = "http://www.w3.org/ns/prov#"
_SEO = "https://seocho.dev/prov#"

def to_ttl(self) -> str:
    """Serialize the run's provenance as a PROV-O Turtle bundle. References facts
    by content-addressed IRI only — the object VALUE is never embedded (so the
    provenance is not itself a leak channel)."""
    import rdflib
    from rdflib import Literal, Namespace, RDF, URIRef, XSD

    PROV, SEO = Namespace(_PROV), Namespace(_SEO)
    g = rdflib.Graph()
    g.bind("prov", PROV)
    g.bind("seocho", SEO)

    run = URIRef(f"{_SEO}run/{self.run_id}")
    agent = URIRef(f"{_SEO}agent/{_canon(self.agent).replace(' ', '_') or 'agent'}")
    doc = URIRef(f"{_SEO}doc/{self.source_doc}")
    plan = URIRef(f"{_SEO}ontology/{self.ontology_version}")

    g.add((run, RDF.type, PROV.Activity))
    g.add((run, PROV.used, doc))
    g.add((run, PROV.used, plan))
    g.add((run, PROV.wasAssociatedWith, agent))
    g.add((run, SEO.workspace, Literal(self.workspace_id)))
    if self.source_platform:
        g.add((run, SEO.sourcePlatform, Literal(self.source_platform)))
    if self.generated_at:
        g.add((run, PROV.startedAtTime, Literal(self.generated_at, datatype=XSD.dateTime)))
    g.add((agent, RDF.type, PROV.SoftwareAgent))
    g.add((doc, RDF.type, PROV.Entity))
    g.add((plan, RDF.type, PROV.Plan))

    for f in self.facts:
        fid = URIRef(f"{_SEO}{f.fact_id(self.workspace_id)}")
        g.add((fid, RDF.type, PROV.Entity))
        g.add((fid, PROV.wasGeneratedBy, run))
        g.add((fid, PROV.wasDerivedFrom, doc))
        g.add((fid, PROV.wasAttributedTo, agent))
        g.add((fid, SEO.confidence, Literal(float(f.confidence), datatype=XSD.decimal)))
        # NOTE: subject/predicate/object are NOT emitted — recover the triple from
        # the graph by fact_id; the provenance stays value-free.
    return g.serialize(format="turtle")
