# Extracted from tgbugs/pyontutils@cb3efcd10f : neurondm/neurondm/build.py
# region: _rest_make_phenotypes (lines 679-743, stratum trav_one_step)
# licence of the source repository: see meta.json
import rdflib
morpho_phenotype =  'ilxtr:MorphologicalPhenotype'
ephys_phenotype = 'ilxtr:ElectrophysiologicalPhenotype'
ilx_base = 'ILX:{:0>7}'

for s, o in sorted(ng.subject_objects(rdflib.RDFS.label))[::-1]:
    spre = ng.namespace_manager.compute_qname(s)[1]
    #if spre.toPython() == g.namespaces['NIFQUAL']:
        #print('skipping', s)
        #continue  # TODO
    if s in new_terms:
        print(s, 'already in as xref probably')
        continue
    #elif spre.toPython() != 'http://uri.interlex.org/base/ilx_' or spre.toPython() != 'http://FIXME.org/' and s.toPython() not in desired_nif_terms:
    #elif spre.toPython() != 'http://FIXME.org/' and s.toPython() not in desired_nif_terms:
        #print('DO NOT WANT', s, spre)
        #continue

    syns = set([s for s in ng.objects(s, dg.namespaces['nsu']['synonym'])])
    #data['syns'] += syns

    data = {}
    id_ = ilx_base.format(ilx_start)
    ilx_start += 1
    if s in s2:
        d = s2[s]
        syns.update(d['syns'])
        new_terms[d['xrefs'][0]] = {'replaced_by':id_}
        xr.add_trip(d['xrefs'][0], 'oboInOwl:replacedBy', id_)
        #dg.add_trip(d['xrefs'][0], 'oboInOwl:replacedBy', id_)
        new_terms[d['xrefs'][1]] = {'replaced_by':id_}
        xr.add_trip(d['xrefs'][1], 'oboInOwl:replacedBy', id_)
        #dg.add_trip(d['xrefs'][1], 'oboInOwl:replacedBy', id_)

        data['labels'] = [d['label'], d['o']]
        #dg.add_trip(id_, rdflib.RDFS.label, d['label'])
        dg.add_trip(id_, rdflib.RDFS.label, d['o'])
        data['xrefs'] = d['xrefs']
        for x in d['xrefs']:  # FIXME... expecting order of evaluation errors here...
            dg.add_trip(id_, 'oboInOwl:hasDbXref', x)  # xr
            xr.add_trip(id_, 'oboInOwl:hasDbXref', x)  # x

    elif (spre.toPython() != 'http://ontology.neuinfo.org/NIF/BiomaterialEntities/NIF-Quality.owl#' or
          ng.namespace_manager.qname(s).replace('default1','NIFQUAL') in desired_nif_terms):  # skip non-xref quals
        #print(ng.namespace_manager.qname(s).replace('default1','NIFQUAL'))
        new_terms[s] = {'replaced_by':id_}
        xr.add_trip(s, 'oboInOwl:replacedBy', id_)
        data['labels'] = [o.toPython()]
        dg.add_trip(id_, rdflib.RDFS.label, o.toPython())
        data['xrefs'] = [s]
        dg.add_trip(id_, 'oboInOwl:hasDbXref', s)  # xr
        xr.add_trip(id_, 'oboInOwl:hasDbXref', s)  # xr
    else:
        ilx_start -= 1
        continue

    new_terms[id_] = data
    dg.add_trip(id_, rdflib.RDF.type, rdflib.OWL.Class)
    xr.add_trip(id_, rdflib.RDF.type, rdflib.OWL.Class)
    for syn in syns:
        if syn.toPython() not in data['labels']:
            if len(syn) > 3:
                dg.add_trip(id_, 'NIFRID:synonym', syn)
            elif syn:
                dg.add_trip(id_, 'NIFRID:abbrev', syn)

    if 'EPHYS' in s or any(['EPHYS' in x for x in data['xrefs']]):
        dg.add_trip(id_, rdflib.RDFS.subClassOf, ephys_phenotype)
    elif 'MORPHOLOGY' in s or any(['MORPHOLOGY' in x for x in data['xrefs']]):
        dg.add_trip(id_, rdflib.RDFS.subClassOf, morpho_phenotype)
