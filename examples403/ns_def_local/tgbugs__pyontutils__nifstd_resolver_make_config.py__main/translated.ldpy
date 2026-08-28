# Extracted from tgbugs/pyontutils@cb3efcd10f : nifstd/resolver/make_config.py
# region: main (lines 17-53, stratum ns_def_local)
# licence of the source repository: see meta.json
import rdflib
from pyontutils.namespaces import PREFIXES as uPREFIXES

def main():
    from docopt import docopt
    args = docopt(__doc__, version='ontload .5')

    ilxtr = rdflib.Namespace(uPREFIXES['ilxtr'])

    prefix = args['--git-local']

    g = rdflib.Graph().parse(f'{prefix}/NIF-Ontology/ttl/generated/NIF-NIFSTD-mapping.ttl', format='turtle')
    with open('ontology-uri-map.conf', 'wt') as f:
        for new, old_ in sorted(g.subject_objects(rdflib.OWL.sameAs), key=lambda a:f'{len(a[1]):0>5}' + a[1]):
            old = old_.split('neuinfo.org', 1)[-1].replace("#","/")
            f.writelines(f'~{old}$ {new};\n')

    ig = rdflib.Graph().parse(f'{prefix}/NIF-Ontology/ttl/generated/NIFSTD-ILX-mapping.ttl', format='turtle')
    with open('uri-ilx-map.conf', 'wt') as f:
        for nif_, ilx in sorted(ig.subject_objects(ilxtr.hasIlxId), key=lambda a:f'{len(a[1]):0>5}' + a[0]):
            nif = nif_.split('neuinfo.org', 1)[-1]
            f.writelines(f'~{nif}$ {ilx};\n')

    sg = rdflib.Graph().parse(f'{prefix}/NIF-Ontology/ttl/generated/NIFSTD-SCR-mapping.ttl', format='turtle')
    with open('uri-scr-map.conf', 'wt') as f:
        for nif_, scr in sorted(sg.subject_objects(ilxtr.hasScrId), key=lambda a:f'{len(a[1]):0>5}' + a[0]):
            nif = nif_.split('neuinfo.org', 1)[-1]
            f.writelines(f'~{nif}$ {scr};\n')

    ilg = (rdflib.Graph()
           .parse(f'{prefix}/NIF-Ontology/ttl/generated/DICOM-ILX-mapping.ttl', format='turtle')
           .parse(f'{prefix}/NIF-Ontology/ttl/generated/NPOKB-ILX-mapping.ttl', format='turtle')
           .parse(f'{prefix}/NIF-Ontology/ttl/generated/PHENOTYPE-CORE-ILX-mapping.ttl', format='turtle')
           .parse(f'{prefix}/NIF-Ontology/ttl/generated/methods-ILX-mapping.ttl', format='turtle')
           .parse(f'{prefix}/NIF-Ontology/ttl/generated/modality-ILX-mapping.ttl', format='turtle')
           .parse(f'{prefix}/NIF-Ontology/ttl/generated/swanson-ILX-mapping.ttl', format='turtle'))
    with open('user-ilx-map.conf', 'wt') as f:
        for user_, ilx in sorted(ilg.subject_objects(ilxtr.hasIlxId), key=lambda a:f'{len(a[1]):0>5}' + a[0]):
            user = user_.split('interlex.org', 1)[-1]
            f.writelines(f'~{user}$ {ilx};\n')
