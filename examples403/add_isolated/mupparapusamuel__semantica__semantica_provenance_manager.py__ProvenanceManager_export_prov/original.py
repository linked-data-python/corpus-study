# Extracted from mupparapusamuel/semantica@873e3aa318 : semantica/provenance/manager.py
# region: ProvenanceManager.export_prov (lines 1276-1307, stratum add_isolated)
# licence of the source repository: see meta.json
if getattr(e, "activity_id", None) and e.activity_id != "unknown":
    act_uri = uri(e.activity_id)
    g.add((act_uri, RDF.type, PROV.Activity))
    g.add((ent_uri, PROV.wasGeneratedBy, act_uri))

    # Typed Activity timing (issue #825, Part B Tier 1)
    if getattr(e, "activity_started_at_time", None):
        g.add((act_uri, PROV.startedAtTime,
               Literal(e.activity_started_at_time, datatype=XSD.dateTime)))
    if getattr(e, "activity_ended_at_time", None):
        g.add((act_uri, PROV.endedAtTime,
               Literal(e.activity_ended_at_time, datatype=XSD.dateTime)))

    # Qualified Generation (issue #825, Part B Tier 1)
    generation = BNode()
    g.add((ent_uri, PROV.qualifiedGeneration, generation))
    g.add((generation, RDF.type, PROV.Generation))
    g.add((generation, PROV.activity, act_uri))
    if getattr(e, "timestamp", None):
        g.add((generation, PROV.atTime, Literal(e.timestamp, datatype=XSD.dateTime)))

    # prov:wasAssociatedWith (issue #825, Part B Tier 2) — direct
    # Activity->Agent link, distinct from the Entity->Agent
    # wasAttributedTo/qualifiedAssociation triples above.
    if ag_uri is not None:
        g.add((act_uri, PROV.wasAssociatedWith, ag_uri))

    # prov:wasInformedBy (issue #825, Part B Tier 2) — chains this
    # activity to prior activities it was informed by (e.g. a
    # pipeline stage informed by the stage before it).
    for informing_id in getattr(e, "informed_by_activities", []):
        g.add((act_uri, PROV.wasInformedBy, uri(informing_id)))
