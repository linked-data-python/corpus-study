# Extracted from LA3D/cogitarelink-solid@49121503ea : tests/test_addressbook_templates.py
# region: test_group_create_template_parses (lines 126-133, stratum trav_one_step)
# licence of the source repository: see meta.json
TMPL = Namespace("https://pod.vardeman.me/vault/ontology/template#")
RDF  = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")

def test_group_create_template_parses():
    g = _load("group-create")
    tmpls = list(g.subjects(RDF.type, TMPL.Template))
    assert len(tmpls) == 1
    tmpl_iri = tmpls[0]
    body = str(next(g.objects(tmpl_iri, TMPL.templateBody)))
    assert "vcard:Group" in body
    assert "vcard:hasMember" in body
