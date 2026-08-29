# Context shim (see meta.json): nodeId_to_iri, idtype2String and is_iri from
# IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/utils.py
# (lines 90-107 and 247-258), so the region executes outside the module.
# Identical bindings for both representations.
import urllib.parse

from rdflib import URIRef


def is_iri(iri):
    # Accepts only if the string starts with 'urn:', 'http://', or 'https://'
    iri_str = str(iri)
    return iri_str.startswith("urn:") or iri_str.startswith("http://") or iri_str.startswith("https://")


def idtype2String(idtype, basens):
    if idtype == basens['numericID']:
        idt = 'i'
    elif idtype == basens['stringID']:
        idt = 's'
    elif idtype == basens['guidID']:
        idt = 'g'
    elif idtype == basens['opaqueID']:
        idt = 'b'
    else:
        idt = 'x'
        print('Warning no idtype found.')
    return idt


def nodeId_to_iri(namespace, basens, nid, idtype, instance_id='', is_entityns=False):
    if instance_id is None:
        instance_id = ''
    quoted_node_id = urllib.parse.quote(nid, safe='')
    idt = idtype2String(idtype, basens)
    if instance_id != '' and is_entityns:
        instance_id = urllib.parse.quote(instance_id, safe='/:')
        if is_iri(instance_id):
            return URIRef(f'{instance_id}node{idt}{quoted_node_id}')
        else:
            return namespace[f'{instance_id}node{idt}{quoted_node_id}']
    return namespace[f'node{idt}{quoted_node_id}']
