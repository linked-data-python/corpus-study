# Extracted from judaicalink/judaicalink-labs@b683b52eaa : labs/data/management/commands/legacy/generate_yivo.py
# region: yivo_rdf (lines 167-187, stratum add_isolated)
# licence of the source repository: see meta.json
import rdflib
import re
from urllib.parse import quote
from ._dataset_command import jlo, jld, skos, dcterms, void, foaf, rdf

def yivo_rdf(graph: rdflib.Graph, resource_dict: dict):
    subject = local(resource_dict["uri"])
    graph.add((subject, jlo.title, rdflib.Literal(resource_dict['title'])))
    graph.add((subject, jlo.describedAt, rdflib.URIRef(resource_dict["uri"])))
    graph.add((subject, skos.prefLabel, rdflib.Literal(resource_dict["title"])))
    for l in resource_dict["links"]:	
            graph.add((subject, skos.related, local(l["href"])))
            if len(l["text"])>0:
                graph.add((local(l["href"]), skos.altLabel, rdflib.Literal(l["text"])))
    graph.add((subject, jlo.hasAbstract, rdflib.Literal(resource_dict["abstract"], "en")))
    for sc in resource_dict["subconcepts"]:
            scu = rdflib.URIRef(str(subject) + "/" + quote(re.sub("[ ]+", "_", sc)))
            graph.add((scu, rdf.type, skos.Concept))
            graph.add((scu, skos.broader, subject))
            graph.add((scu, skos.prefLabel, rdflib.Literal(sc)))
            graph.add((subject, skos.narrower, scu))
    for sr in resource_dict["subrecords"]:
            graph.add((subject, skos.narrower, local(sr.href)))
    if "broader" in resource_dict:
            graph.add((subject, skos.broader, rdflib.URIRef(resource_dict["broader"])))
    return graph
