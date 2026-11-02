# Extracted from adobe/aepp@05c73dfc6d : aepp/knowledgegraph.py
# region: KnowledgeGraph.buildGraph (lines 273-360, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, XSD, DCAT, DCTERMS
from rdflib import Graph, Namespace, Literal,URIRef

# Wrapped in a function (context restoration, meta.json: this is one of the
# regions with no visible graph -- kwargs/df_datasets/graph/*_NODE/
# *_flow_managers/audiences are all free variables of the original method
# body). The body itself, from here to the end of the file, is byte-for-byte
# what was extracted.
def build_graph_region(self, kwargs, df_datasets, graph, CATALOG_NODE,
                        PROFILE_NODE, FLOWS_NODE, AUDIENCES_NODE,
                        source_flow_managers, audiences,
                        destination_flow_managers):
 if kwargs.get('only_schema',False) == False:
    for index, row in df_datasets.iterrows():
        dataset = self.CATALOG[row['id']]
        graph += [(CATALOG_NODE, self.CATALOG.contains, dataset),
                  (dataset, RDF.type, DCAT.Dataset),
                  (dataset, self.SCHEMA.implements, URIRef(row['schemaId'])),
                  (dataset, DCTERMS.title, Literal(row.get('name'))),
                  (dataset, self.CATALOG.rows,
                   Literal(row.get('datalake_rows'), datatype=XSD.integer))]
        if row['profileEnabled']:
            graph += [(PROFILE_NODE, self.PROFILE.contains, dataset),
                      (dataset, self.PROFILE.linked, PROFILE_NODE),
                      (dataset, self.PROFILE.participates, self.PROFILE.UPS)]
        if row['identityEnabled']:
            graph += [(dataset, self.PROFILE.linked, PROFILE_NODE),
                      (dataset, self.PROFILE.participates, self.PROFILE.UIS)]
    for element in self.__dataset_preview__:
        graph += [(self.CATALOG[element.get('value')], self.PROFILE.counts,
                   Literal(element.get('fullIDsCount'), datatype=XSD.integer)),
                  (self.CATALOG[element.get('datasetId')], self.PROFILE.participates, self.PROFILE.UPS)]
    graph.add((FLOWS_NODE, self.FLOWS.contains, self.FLOWS.SourceFlows))
    for flow in source_flow_managers:
        if getattr(flow, 'datasetId', None) is not None and flow.datasetId in df_datasets['id'].tolist():
            flow_node = self.FLOWS[flow.id]
            graph += [(self.FLOWS.SourceFlows, self.FLOWS.contains, flow_node),
                      (flow_node, RDFS.label, Literal(flow.name)),
                      (flow_node, RDF.type, Literal('IngestionFlow')),
                      (flow_node, self.FLOWS.loads, self.CATALOG[flow.datasetId])]
            if flow.frequency is not None:
                graph.add((flow_node, self.FLOWS.frequency, Literal(flow.frequency)))
    if kwargs.get('verbose',False) == True:
        print("  --Audiences")
    for audience in audiences:
        audience_node = self.AUDIENCES[audience['id']]
        graph += [(AUDIENCES_NODE, self.AUDIENCES.contains, audience_node),
                  (audience_node, RDFS.label, Literal(audience.get('name'))),
                  (audience_node, RDF.type, self.AUDIENCES.audience)]
        evaluationInfo = audience.get('evaluationInfo',{})
        for mode, evaluation in (('batch', "BATCH"), ('continuous', "STREAMING"),
                                 ('synchronous', "EDGE")):
            if evaluationInfo.get(mode,{}).get('enabled',False):
                graph.add((audience_node, self.AUDIENCES.evaluation, Literal(evaluation)))
        for path in self.segmentationAPI.extractPaths(audience) or []:
            if '@' not in path and path != 'xEvent':
                if path.startswith('xEvent.'):
                    path = path.replace('xEvent.','')
                else:
                    graph.add((audience_node, self.AUDIENCES.behavior, Literal("Profile-based")))
                node = self.SCHEMA[path.replace('{}', '').replace('[]', '')]
                if (node, RDF.type, self.SCHEMA.path) not in graph:
                    graph += [(node, RDF.type, self.SCHEMA.path),
                              (node, self.SCHEMA.usedIn, RDF.nil)]
                graph.add((node, self.AUDIENCES.usedIn, audience_node))
            if path == 'xEvent':
                graph += [(audience_node, self.AUDIENCES.behavior, Literal("Event-based")),
                          (self.SCHEMA.xEvent, self.AUDIENCES.usedIn, audience_node),
                          (self.SCHEMA.xEvent, self.SCHEMA.usedIn, RDF.nil)]
            if '@' in path:
                graph.add((audience_node, self.AUDIENCES.behavior, Literal("Relationship-based")))
    if kwargs.get('verbose',False) == True:
        print("  --Flows")
    graph.add((FLOWS_NODE, self.FLOWS.contains, self.FLOWS.DestinationFlows))
    for destination in destination_flow_managers:
        destination_node = self.FLOWS[destination.id]
        graph += [(self.FLOWS.DestinationFlows, self.FLOWS.contains, destination_node),
                  (destination_node, RDF.type, Literal('DestinationFlow')),
                  (destination_node, RDFS.label, Literal(destination.name)),
                  (destination_node, self.FLOWS.frequency, Literal(destination.frequency))]
        for key, value in destination.attributes.items():
            node = self.SCHEMA[key.replace('{}', '').replace('[]', '')]
            graph += [(node, self.FLOWS.usedIn, destination_node),
                      (destination_node, self.FLOWS.sharedAttributes, node)]
            if value.get('primary',False) == True:
                graph.add((destination_node, self.FLOWS.primaryAttributes, node))
            if value.get('mandatory',False) == True:
                graph.add((destination_node, self.FLOWS.mandatoryAttributes, node))
        for audienceId in destination.audiences:
            graph += [(destination_node, self.FLOWS.audiences, self.AUDIENCES[audienceId]),
                      (self.AUDIENCES[audienceId], self.FLOWS.usedIn, destination_node)]
    self.global_graph = graph
 return graph
