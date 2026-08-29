# Extracted from isaacgravenor/neo-galacteek@e201b39d78 : galacteek/ld/rdf/guardian.py
# region: GuardianTriggerAction.captchaVcProcess (lines 143-206, stratum add_isolated)
# licence of the source repository: see meta.json
import json
from rdflib import Graph
from rdflib import URIRef
from galacteek.ipfs import ipfsOp

@ipfsOp
async def captchaVcProcess(self, ipfsop, src: Graph, dst: Graph, s, p, o):
    issuer = src.value(
        subject=s,
        predicate=URIRef('ips://galacteek.ld/issuer')
    )

    beneficiary = src.value(
        subject=s,
        predicate=URIRef('ips://galacteek.ld/credentialSubject')
    )

    proofuri = src.value(
        subject=s,
        predicate=URIRef('ips://galacteek.ld/proof')
    )

    proof = src.resource(proofuri)

    vmethod = proof.value(
        p=URIRef('ips://galacteek.ld/verificationMethod')
    )

    jws = str(proof.value(
        p=URIRef('ips://galacteek.ld/jws')
    ))

    pem = str(dst.value(
        subject=vmethod,
        predicate=URIRef('https://w3id.org/security#publicKeyPem')
    ))

    rsaAgent = ipfsop.rsaAgent

    key = await rsaAgent.rsaExec.importKey(str(pem))
    if not key:
        return

    payload = await rsaAgent.rsaExec.jwsVerifyFromPem(jws, pem)
    if not payload:
        raise Exception(f'Invalid captcha VC: {s}')

    obj = json.loads(payload)

    if 0:
        dst.add((
            issuer,
            URIRef('ips://galacteek.ld/didCaptchaTrusts'),
            beneficiary
        ))

    dst.remove((
        beneficiary,
        URIRef('ips://galacteek.ld/activeTrustToken'),
        None
    ))

    dst.add((
        beneficiary,
        URIRef('ips://galacteek.ld/activeTrustToken'),
        URIRef(obj.get('id'))
    ))

    return obj
