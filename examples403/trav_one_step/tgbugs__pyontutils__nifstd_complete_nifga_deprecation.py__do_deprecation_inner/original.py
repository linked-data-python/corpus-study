# Extracted from tgbugs/pyontutils@cb3efcd10f : nifstd/complete/nifga_deprecation.py
# region: do_deprecation.inner (lines 162-271, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import URIRef, RDFS, RDF, OWL
from rdflib.namespace import SKOS
from IPython import embed
sgg = Graph(cache=True)
sgv = Vocabulary(cache=True)
preflabs = (  # pulled from conflated
    'NIFGA:birnlex_2596',
    'NIFGA:birnlex_4101',
    'NIFGA:birnlex_1184',
    'NIFGA:birnlex_703',
    'NIFGA:birnlex_1117',
    'NIFGA:nlx_143552',
    'NIFGA:birnlex_1341',
    'NIFGA:birnlex_1335',
    'NIFGA:birnlex_1400',
    'NIFGA:birnlex_1519',  # NOTE: nerve root and nerve fiber bundle are being conflated...
    'NIFGA:birnlex_1277',
    'NIFGA:birnlex_2523',
    'NIFGA:birnlex_2528',  # a real exact duple with 2529 apparently
    'NIFGA:birnlex_2651',  # a real exact duple with 2654 apparently
    'NIFGA:nlx_anat_20081224',  # other option is 'NIFGA:birnlex_932' -> Lingula
    'NIFGA:nlx_anat_20081235',  # other option is 'NIFGA:birnlex_1165' -> Nodulus
    'NIFGA:birnlex_1588',
    'NIFGA:birnlex_1106',
    'NIFGA:birnlex_1582',
    'NIFGA:birnlex_1589',
    'NIFGA:birnlex_1414',
    'NIFGA:birnlex_4081',
)
anns_to_port = []  # (SKOS.prefLabel, )  # skipping this for now :/

def inner(nifga, uberon):
    # check neuronames id TODO

    udepr = sgv.findById(uberon)['deprecated'] if uberon != 'NOREP' else False
    if udepr:
        # add xref to the now deprecated uberon term
        graph.add_trip(nifga, 'oboInOwl:hasDbXref', uberon)
        #print('Replacement is deprecated, not replacing:', uberon)
        graph.add_trip(nifga, RDFS.comment, 'xref %s is deprecated, so not using replacedBy:' % uberon)
    else:
        # add replaced by -> uberon
        graph.add_trip(nifga, 'replacedBy:', uberon)

    # add deprecated true (ok to do twice...)
    graph.add_trip(nifga, OWL.deprecated, True)

    # review nifga relations, specifically has_proper_part, proper_part_of
    # put those relations on the uberon term in the
    # if there is no uberon term raise an error so we can look into it

    #if uberon not in uedges:
        #uedges[uberon] = defaultdict(set)
    resp = sgg.getNeighbors(nifga)
    edges = resp['edges']
    if nifga in additional_edges:
        edges.append(additional_edges[nifga])
    include = False  # set this to True when running anns
    for edge in edges:  # FIXME TODO hierarchy extraction and porting
        #print(edge)
        if udepr:  # skip everything if uberon is deprecated
            include = False
            hier = False
            break
        sub = edge['sub']
        obj = edge['obj']
        pred = edge['pred']
        hier = False
        if pred == 'subClassOf':
            pred = RDFS.subClassOf
            continue
        elif pred == 'equivalentClass':
            pred = OWL.equivalentClass
            continue
        elif pred == 'isDefinedBy':
            pred = RDFS.isDefinedBy
            continue
        elif pred == 'http://www.obofoundry.org/ro/ro.owl#has_proper_part':
            hier = True
            include = True
        elif pred == 'http://www.obofoundry.org/ro/ro.owl#proper_part_of':
            hier = True
            include = True
        elif pred == 'ilx:partOf':
            hier = True
            include = True

        if sub == nifga:
            try:
                obj = replaced_by[obj]
                if obj == 'NOREP':
                    hier = False
            except KeyError:
                print('not in replaced_by', obj)
            if type(obj) == tuple: continue  # TODO
            if hier:
                if uberon not in uedges[obj][pred]:
                    uedges[obj][pred].add(uberon)
                    bridge.add_hierarchy(obj, pred, uberon)
            else:
                #bridge.add_trip(uberon, pred, obj)
                pass
        elif obj == nifga:
            try:
                sub = replaced_by[sub]
                if sub == 'NOREP':
                    hier = False
            except KeyError:
                print('not in replaced_by', sub)
            if type(sub) == tuple: continue  # TODO
            if hier:
                if sub not in uedges[uberon][pred]:
                    uedges[uberon][pred].add(sub)
                    bridge.add_hierarchy(uberon, pred, sub)
            else:
                #bridge.add_trip(sub, pred, uberon)
                pass

    if False and uberon not in udone and include:  # skip porting annotations and labels for now
        #udone.add(uberon)
        try:
            label = sgv.findById(uberon)['labels'][0]
        except IndexError:
            WAT = sgv.findById(uberon)
            embed()
        bridge.add_class(uberon, label=label)

        # annotations to port
        for p in anns_to_port:
            os_ = list(graph.g.objects(graph.expand(nifga), p))
            for o in os_:
                if label.lower() != o.lower():  # we can simply capitalize labels
                    print(label.lower())
                    print(o.lower())
                    print()
                    bridge.add_trip(uberon, p, o)

            if p == SKOS.prefLabel and not os_:
                if uberon not in conflated or (uberon in conflated and nifga in preflabs):
                    l = list(graph.g.objects(graph.expand(nifga), RDFS.label))[0]
                    bridge.add_trip(uberon, SKOS.prefLabel, l)  # port label to prefLabel if no prefLabel
