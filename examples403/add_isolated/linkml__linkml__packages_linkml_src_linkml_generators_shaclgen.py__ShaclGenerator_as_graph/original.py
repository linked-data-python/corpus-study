# Extracted from linkml/linkml@680595df54 : packages/linkml/src/linkml/generators/shaclgen.py
# region: ShaclGenerator.as_graph (lines 314-399, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from rdflib.namespace import RDF, RDFS, SH, XSD
from linkml_runtime.utils.yamlutils import TypedNode, extended_float, extended_int, extended_str

if s.any_of:
    # It is not allowed to use any of and equals_string or equals_string_in in one
    # slot definition, as both are mapped to sh:in in SHACL
    if s.equals_string or s.equals_string_in:
        error = "'equals_string'/'equals_string_in' and 'any_of' are mutually exclusive"
        raise ValueError(f"{TypedNode.yaml_loc(str(s), suffix='')} {error}")

    or_node = BNode()
    prop_pv(SH["or"], or_node)
    range_list = []
    for any in s.any_of:
        r = any.range
        if r in all_classes:
            class_node = BNode()

            def cl_node_pv(p, v):
                if v is not None:
                    g.add((class_node, p, v))

            self._add_class(cl_node_pv, r)
            range_list.append(class_node)
        elif r in sv.all_types():
            t_node = BNode()

            def t_node_pv(p, v):
                if v is not None:
                    g.add((t_node, p, v))

            self._add_type(t_node_pv, r)
            range_list.append(t_node)
        elif r in sv.all_enums():
            en_node = BNode()

            def en_node_pv(p, v):
                if v is not None:
                    g.add((en_node, p, v))

            self._add_enum(g, en_node_pv, r)
            range_list.append(en_node)
        else:
            st_node = BNode()

            def st_node_pv(p, v):
                if v is not None:
                    g.add((st_node, p, v))

            add_simple_data_type(st_node_pv, r)
            range_list.append(st_node)
    Collection(g, or_node, range_list)
else:
    prop_pv_literal(SH.hasValue, s.equals_number)
    r = s.range
    if s.equals_string or s.equals_string_in:
        # Check if range is "string" as this is mandatory for "equals_string" and "equals_string_in"
        if r != "string":
            raise ValueError(
                f"slot: \"{slot_uri}\" - 'equals_string' and 'equals_string_in'"
                f" require range 'string' and not '{r}'"
            )

    if r in all_classes:
        cls_def = sv.get_class(r)
        is_any = cls_def and getattr(cls_def, "class_uri", None) == "linkml:Any"
        self._add_class(prop_pv, r)
        if not is_any:
            if sv.get_identifier_slot(r) is not None:
                prop_pv(SH.nodeKind, SH.IRI)
            else:
                prop_pv(SH.nodeKind, SH.BlankNodeOrIRI)
    elif r in sv.all_types():
        self._add_type(prop_pv, r)
    elif r in sv.all_enums():
        self._add_enum(g, prop_pv, r)
    else:
        add_simple_data_type(prop_pv, r)
    if s.pattern:
        prop_pv(SH.pattern, Literal(s.pattern))
    if s.equals_string:
        # Map equal_string and equal_string_in to sh:in
        self._and_equals_string(g, prop_pv, [s.equals_string])
    if s.equals_string_in:
        # Map equal_string and equal_string_in to sh:in
        self._and_equals_string(g, prop_pv, s.equals_string_in)
    if self.expand_subproperty_of and s.subproperty_of:
        # Map subproperty_of to sh:in with slot descendants
        self._add_subproperty_constraint(g, prop_pv, s)
