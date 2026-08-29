# Extracted from adobe/aepp@05c73dfc6d : aepp/knowledgegraph.py
# region: KnowledgeGraph.buildGraph (lines 273-360, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, XSD, DCAT, DCTERMS
from rdflib import Graph, Namespace, Literal,URIRef

if kwargs.get('only_schema',False) == False:
    for index, row in df_datasets.iterrows():
        graph.add((CATALOG_NODE, self.CATALOG.contains, self.CATALOG[row['id']]))
        graph.add((self.CATALOG[row['id']], RDF.type, DCAT.Dataset))
        graph.add((self.CATALOG[row['id']], self.SCHEMA.implements, URIRef(row['schemaId'])))
        graph.add((self.CATALOG[row['id']], DCTERMS.title, Literal((row.get('name')))))
        graph.add((self.CATALOG[row['id']], self.CATALOG.rows, Literal(row.get('datalake_rows'),datatype=XSD.integer)))
        if row['profileEnabled']:
            graph.add((PROFILE_NODE,self.PROFILE.contains,self.CATALOG[row['id']]))
            graph.add((self.CATALOG[row['id']],self.PROFILE.linked, PROFILE_NODE))
            graph.add((self.CATALOG[row['id']],self.PROFILE.participates,self.PROFILE.UPS))
        if row['identityEnabled']:
            graph.add((self.CATALOG[row['id']],self.PROFILE.linked, PROFILE_NODE))
            graph.add((self.CATALOG[row['id']],self.PROFILE.participates,self.PROFILE.UIS))
    for element in self.__dataset_preview__:
        graph.add((self.CATALOG[element.get('value')],self.PROFILE.counts, Literal(element.get('fullIDsCount'),datatype=XSD.integer)))
        graph.add((self.CATALOG[element.get('datasetId')],self.PROFILE.participates,self.PROFILE.UPS))
    graph.add((FLOWS_NODE, self.FLOWS.contains, self.FLOWS.SourceFlows))
    for flow in source_flow_managers:
        if hasattr(flow, 'datasetId'):
            if flow.datasetId is not None and flow.datasetId in df_datasets['id'].tolist():
                graph.add((self.FLOWS.SourceFlows, self.FLOWS.contains, self.FLOWS[flow.id]))
                graph.add((self.FLOWS[flow.id], RDFS.label, Literal(flow.name)))
                graph.add((self.FLOWS[flow.id], RDF.type, Literal('IngestionFlow')))
                graph.add((self.FLOWS[flow.id], self.FLOWS.loads, self.CATALOG[flow.datasetId]))
                if flow.frequency is not None:
                    graph.add((self.FLOWS[flow.id], self.FLOWS.frequency, Literal(flow.frequency)))
    if kwargs.get('verbose',False) == True:
        print(f"  --Audiences")
    for audience in audiences:
        graph.add((AUDIENCES_NODE, self.AUDIENCES.contains, self.AUDIENCES[audience['id']]))
        graph.add((self.AUDIENCES[audience['id']], RDFS.label, Literal(audience.get('name'))))
        graph.add((self.AUDIENCES[audience['id']], RDF.type, self.AUDIENCES.audience))
        evaluationInfo = audience.get('evaluationInfo',{})
        if evaluationInfo.get('batch',{}).get('enabled',False):
            graph.add((self.AUDIENCES[audience['id']], self.AUDIENCES.evaluation, Literal("BATCH")))
        if evaluationInfo.get('continuous',{}).get('enabled',False):
            graph.add((self.AUDIENCES[audience['id']], self.AUDIENCES.evaluation, Literal("STREAMING")))
        if evaluationInfo.get('synchronous',{}).get('enabled',False):
            graph.add((self.AUDIENCES[audience['id']], self.AUDIENCES.evaluation, Literal("EDGE")))
        paths = self.segmentationAPI.extractPaths(audience)
        if paths is not None:
            for path in paths:
                if '@' not in path and path != 'xEvent':
                    if path.startswith('xEvent.'):
                        path = path.replace('xEvent.','')
                    else:
                        if (self.AUDIENCES[audience['id']], self.AUDIENCES.behavior, Literal("Profile-based")) not in graph:
                            graph.add((self.AUDIENCES[audience['id']], self.AUDIENCES.behavior, Literal("Profile-based")))
                    node = self.SCHEMA[path.replace('{}', '').replace('[]', '')]
                    if (node, RDF.type, self.SCHEMA.path) in graph:
                        graph.add((node, self.AUDIENCES.usedIn, self.AUDIENCES[audience['id']]))
                    else:
                        graph.add((node, RDF.type, self.SCHEMA.path))
                        graph.add((node, self.AUDIENCES.usedIn, self.AUDIENCES[audience['id']]))
                        graph.add((node, self.SCHEMA.usedIn, RDF.nil))
                if path == 'xEvent':
                    node = self.SCHEMA[path.replace('{}', '').replace('[]', '')]
                    graph.add((self.AUDIENCES[audience['id']], self.AUDIENCES.behavior, Literal("Event-based")))
                    graph.add((node, self.AUDIENCES.usedIn, self.AUDIENCES[audience['id']]))
                    graph.add((node, self.SCHEMA.usedIn, RDF.nil))
                if '@' in path:
                    graph.add((self.AUDIENCES[audience['id']], self.AUDIENCES.behavior, Literal("Relationship-based")))
    if kwargs.get('verbose',False) == True:
        print(f"  --Flows")
    graph.add((FLOWS_NODE, self.FLOWS.contains, self.FLOWS.DestinationFlows))
    for destination in destination_flow_managers:
        graph.add((self.FLOWS.DestinationFlows, self.FLOWS.contains, self.FLOWS[destination.id]))
        graph.add((self.FLOWS[destination.id], RDF.type, Literal('DestinationFlow')))
        graph.add((self.FLOWS[destination.id], RDFS.label, Literal(destination.name)))
        graph.add((self.FLOWS[destination.id], self.FLOWS.frequency, Literal(destination.frequency)))
        if len(destination.attributes)>0:
            for key, value in destination.attributes.items():
                node = self.SCHEMA[key.replace('{}', '').replace('[]', '')]
                graph.add((node, self.FLOWS.usedIn, self.FLOWS[destination.id]))
                graph.add((self.FLOWS[destination.id], self.FLOWS.sharedAttributes, node))
                if value.get('primary',False) == True:
                    graph.add((self.FLOWS[destination.id], self.FLOWS.primaryAttributes, node))
                if value.get('mandatory',False) == True:
                    graph.add((self.FLOWS[destination.id], self.FLOWS.mandatoryAttributes, node))
        if len(destination.audiences)>0:
            for audienceId in destination.audiences:
                graph.add((self.FLOWS[destination.id], self.FLOWS.audiences, self.AUDIENCES[audienceId]))
                graph.add((self.AUDIENCES[audienceId], self.FLOWS.usedIn, self.FLOWS[destination.id]))
    self.global_graph = graph
    return self.global_graph
else:
    return graph
