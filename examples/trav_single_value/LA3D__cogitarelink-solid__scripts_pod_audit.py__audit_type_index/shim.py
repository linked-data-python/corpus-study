# Context shim (see meta.json): the two pure helpers `audit_type_index`
# calls, copied verbatim from scripts/pod_audit.py in
# LA3D/cogitarelink-solid@49121503ea, so the region executes outside its
# script. Identical bindings for both representations. Neither performs
# network I/O -- the region's own network call (`await client.get(ti_url)`)
# happens BEFORE the extracted lines (see original.py's docstring).
def finding(sev, location, constraint, message, remediation=""):
    return dict(severity=sev, location=str(location), constraint=constraint,
                message=message.strip(), remediation=remediation)


def rewrite(iri, canon_base, pod_base):
    "Map a canonical-IRI to the reachable Pod base for HTTP cross-checks."
    return pod_base + iri[len(canon_base):] if iri.startswith(canon_base) else iri
