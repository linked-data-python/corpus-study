# Extracted from philbarker/TAP2SHACL@910ab540e2 : src/ap2shacl/ap2shaclConverter.py
# region: AP2SHACLConverter.convert_statementTemplates (lines 224-305, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Literal, BNode, Namespace
from rdflib import SH, RDF, RDFS, XSD, SDO
from urllib.parse import quote

def convert_statementTemplates(self):
    """Add the property statements from the application profile to the SHACL graph as property shapes."""
    # TODO: untangle this : there must be repeats that can be factored out
    # TODO: fix case when there are > 1 properties in template
    for ps in self.ap.statementTemplates:
        if len(ps.properties) > 1:  # Unusual case of alternative property paths
            print(
                "# Warning: property template with multiple properties is not fully supported."
            )
            ps_ids = []
            severity = self.convert_severity(ps.severity)
            for p in ps.properties:
                # TODO this needs revisting, half the elements aren't processed
                prop = quote(p.replace("#", "").replace(":", "_"))
                ps_name = make_property_shape_name(ps) + "_" + prop + "_opt"
                ps_id = str2URIRef(self.ap.namespaces, ps_name)
                ps_ids.append(ps_id)
                ps_opt_uri = str2URIRef(self.ap.namespaces, ps_name)
                path = str2URIRef(self.ap.namespaces, p)
                self.sg.add((ps_opt_uri, RDF.type, SH.PropertyShape))
                self.sg.add((ps_opt_uri, SH.path, path))
                if ps.mandatory:
                    self.sg.add((ps_opt_uri, SH.minCount, Literal(1)))
                if not ps.repeatable:
                    self.sg.add((ps_opt_uri, SH.maxCount, Literal(1)))
                if severity:
                    self.sg.add(((ps_opt_uri, SH.severity, severity)))
            or_list = list2RDFList(self.sg, ps_ids, "URIRef", self.ap.namespaces)
            for sh in ps.shapes:
                self.sg.add(
                    (str2URIRef(self.ap.namespaces, sh), SH.property, ps_opt_uri)
                )
        else:  # Normal case of just one property path
            ps_name = make_property_shape_name(ps)
            severity = self.convert_severity(ps.severity)
            ps_uri = str2URIRef(self.ap.namespaces, ps_name)
            for sh in ps.shapes:
                self.sg.add(
                    (str2URIRef(self.ap.namespaces, sh), SH.property, ps_uri)
                )
            self.sg.add((ps_uri, RDF.type, SH.PropertyShape))
            for lang in ps.labels:
                name = Literal(ps.labels[lang], lang=lang)
                self.sg.add((ps_uri, SH.name, name))
            for lang in ps.notes:
                note = Literal(ps.notes[lang], lang=lang)
                self.sg.add((ps_uri, RDFS.comment, note))
            for lang in ps.propertyDescriptions:
                descr = Literal(ps.propertyDescriptions[lang], lang=lang)
                self.sg.add((ps_uri, SH.description, descr))
            for property in ps.properties:
                path = str2URIRef(self.ap.namespaces, property)
                self.sg.add((ps_uri, SH.path, path))
            for lang in ps.message:
                message = Literal(ps.message[lang], lang=lang)
                self.sg.add((ps_uri, SH.message, message))
            if severity:
                self.sg.add(((ps_uri, SH.severity, severity)))
            if ps.valueNodeTypes != []:
                nodeKind = convert_nodeKind(ps.valueNodeTypes)
                if nodeKind is not None:
                    self.sg.add((ps_uri, SH.nodeKind, nodeKind))
            if ps.valueDataTypes != []:
                (shProp, val) = self.convert_valueDataTypes(ps.valueDataTypes)
                self.sg.add((ps_uri, shProp, val))
            if ps.valueConstraints != []:
                constr_dict = self.convert_valConstraints(ps)
                for constr_type in constr_dict.keys():
                    for c in constr_dict[constr_type]:
                        self.sg.add((ps_uri, constr_type, c))
            else:  # no value constraints to add
                pass
            if ps.valueShapes != []:
                (shProp, val) = self.convert_valueShapes(ps.valueShapes)
                self.sg.add((ps_uri, shProp, val))
            if ps.valueClasses != []:
                (shProp, val) = self.convert_valueClasses(ps.valueClasses)
                self.sg.add((ps_uri, shProp, val))
            if ps.mandatory:
                self.sg.add((ps_uri, SH.minCount, Literal(1)))
            if not ps.repeatable:
                self.sg.add((ps_uri, SH.maxCount, Literal(1)))
