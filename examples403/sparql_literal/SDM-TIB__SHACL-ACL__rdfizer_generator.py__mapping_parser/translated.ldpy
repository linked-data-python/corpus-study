# Extracted from SDM-TIB/SHACL-ACL@363238e256 : rdfizer/generator.py
# region: mapping_parser (lines 636-735, stratum sparql_literal)
# licence of the source repository: see meta.json
from rdflib.plugins.sparql import prepareQuery

for result_triples_map in mapping_query_results:
	triples_map_exists = False
	for triples_map in triples_map_list:
		triples_map_exists = triples_map_exists or (str(triples_map.triples_map_id) == str(result_triples_map.triples_map_id))

	subject_map = None
	if result_triples_map.jdbcDSN is not None:
		jdbcDSN = result_triples_map.jdbcDSN
		jdbcDriver = result_triples_map.jdbcDriver
	if not triples_map_exists:
		if result_triples_map.subject_template is not None:
			if result_triples_map.rdf_class is None:
				reference, condition = string_separetion(str(result_triples_map.subject_template))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_template), condition, "template", [result_triples_map.rdf_class], result_triples_map.termtype, [result_triples_map.graph])
			else:
				reference, condition = string_separetion(str(result_triples_map.subject_template))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_template), condition, "template", [str(result_triples_map.rdf_class)], result_triples_map.termtype, [result_triples_map.graph])
		elif result_triples_map.subject_reference is not None:
			if result_triples_map.rdf_class is None:
				reference, condition = string_separetion(str(result_triples_map.subject_reference))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_reference), condition, "reference", [result_triples_map.rdf_class], result_triples_map.termtype, [result_triples_map.graph])
			else:
				reference, condition = string_separetion(str(result_triples_map.subject_reference))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_reference), condition, "reference", [str(result_triples_map.rdf_class)], result_triples_map.termtype, [result_triples_map.graph])
		elif result_triples_map.subject_constant is not None:
			if result_triples_map.rdf_class is None:
				reference, condition = string_separetion(str(result_triples_map.subject_constant))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_constant), condition, "constant", [result_triples_map.rdf_class], result_triples_map.termtype, [result_triples_map.graph])
			else:
				reference, condition = string_separetion(str(result_triples_map.subject_constant))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_constant), condition, "constant", [str(result_triples_map.rdf_class)], result_triples_map.termtype, [result_triples_map.graph])
		elif result_triples_map.subject_function is not None:
			if result_triples_map.rdf_class is None:
				reference, condition = string_separetion(str(result_triples_map.subject_constant))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_function), condition, "function", [result_triples_map.rdf_class], result_triples_map.termtype, [result_triples_map.graph])
			else:
				reference, condition = string_separetion(str(result_triples_map.subject_constant))
				subject_map = tm.SubjectMap(str(result_triples_map.subject_function), condition, "function", [str(result_triples_map.rdf_class)], result_triples_map.termtype, [result_triples_map.graph])

		mapping_query_prepared = prepareQuery(mapping_query)


		mapping_query_prepared_results = mapping_graph.query(mapping_query_prepared, initBindings={'triples_map_id': result_triples_map.triples_map_id})




		predicate_object_maps_list = []

		function = False
		for result_predicate_object_map in mapping_query_prepared_results:

			if result_predicate_object_map.predicate_constant is not None:
				predicate_map = tm.PredicateMap("constant", str(result_predicate_object_map.predicate_constant), "")
			elif result_predicate_object_map.predicate_constant_shortcut is not None:
				predicate_map = tm.PredicateMap("constant shortcut", str(result_predicate_object_map.predicate_constant_shortcut), "")
			elif result_predicate_object_map.predicate_template is not None:
				template, condition = string_separetion(str(result_predicate_object_map.predicate_template))
				predicate_map = tm.PredicateMap("template", template, condition)
			elif result_predicate_object_map.predicate_reference is not None:
				reference, condition = string_separetion(str(result_predicate_object_map.predicate_reference))
				predicate_map = tm.PredicateMap("reference", reference, condition)
			else:
				predicate_map = tm.PredicateMap("None", "None", "None")

			if "execute" in predicate_map.value:
				function = True

			if result_predicate_object_map.object_constant is not None:
				object_map = tm.ObjectMap("constant", str(result_predicate_object_map.object_constant), str(result_predicate_object_map.object_datatype), "None", "None", result_predicate_object_map.term, result_predicate_object_map.language)
			elif result_predicate_object_map.object_template is not None:
				object_map = tm.ObjectMap("template", str(result_predicate_object_map.object_template), str(result_predicate_object_map.object_datatype), "None", "None", result_predicate_object_map.term, result_predicate_object_map.language)
			elif result_predicate_object_map.object_reference is not None:
				object_map = tm.ObjectMap("reference", str(result_predicate_object_map.object_reference), str(result_predicate_object_map.object_datatype), "None", "None", result_predicate_object_map.term, result_predicate_object_map.language)
			elif result_predicate_object_map.object_parent_triples_map is not None:
				if (result_predicate_object_map.child_function is not None) and (result_predicate_object_map.parent_function is not None):
					object_map = tm.ObjectMap("parent triples map function", str(result_predicate_object_map.object_parent_triples_map), str(result_predicate_object_map.object_datatype), str(result_predicate_object_map.child_function), str(result_predicate_object_map.parent_function), result_predicate_object_map.term, result_predicate_object_map.language)
				elif (result_predicate_object_map.child_function is None) and (result_predicate_object_map.parent_function is not None):
					object_map = tm.ObjectMap("parent triples map parent function", str(result_predicate_object_map.object_parent_triples_map), str(result_predicate_object_map.object_datatype), str(result_predicate_object_map.child_function), str(result_predicate_object_map.parent_value), result_predicate_object_map.term, result_predicate_object_map.language)
				elif (result_predicate_object_map.child_function is not None) and (result_predicate_object_map.parent_function is None):
					object_map = tm.ObjectMap("parent triples map child function", str(result_predicate_object_map.object_parent_triples_map), str(result_predicate_object_map.object_datatype), str(result_predicate_object_map.child_value), str(result_predicate_object_map.parent_function), result_predicate_object_map.term, result_predicate_object_map.language)
				else:
					object_map = tm.ObjectMap("parent triples map", str(result_predicate_object_map.object_parent_triples_map), str(result_predicate_object_map.object_datatype), str(result_predicate_object_map.child_value), str(result_predicate_object_map.parent_value), result_predicate_object_map.term, result_predicate_object_map.language)
			elif result_predicate_object_map.object_constant_shortcut is not None:
				object_map = tm.ObjectMap("constant shortcut", str(result_predicate_object_map.object_constant_shortcut), str(result_predicate_object_map.object_datatype), "None", "None", result_predicate_object_map.term, result_predicate_object_map.language)
			elif result_predicate_object_map.function is not None:
				object_map = tm.ObjectMap("reference function", str(result_predicate_object_map.function),str(result_predicate_object_map.object_datatype), "None", "None", result_predicate_object_map.term, result_predicate_object_map.language)
			else:
				object_map = tm.ObjectMap("None", "None", "None", "None", "None", "None", "None")

			predicate_object_maps_list += [tm.PredicateObjectMap(predicate_map, object_map)]

		if function:
			current_triples_map = tm.TriplesMap(str(result_triples_map.triples_map_id), str(result_triples_map.data_source), None, predicate_object_maps_list, ref_form=str(result_triples_map.ref_form), iterator=str(result_triples_map.iterator), tablename=str(result_triples_map.tablename), query=str(result_triples_map.query),function=True)
		else:
			if result_triples_map.url_source is not None:
				current_triples_map = tm.TriplesMap(str(result_triples_map.triples_map_id), str(result_triples_map.url_source), subject_map, predicate_object_maps_list, ref_form=str(result_triples_map.ref_form), iterator=str(result_triples_map.iterator), tablename=str(result_triples_map.tablename), query=str(result_triples_map.query),function=False)
			else:
				current_triples_map = tm.TriplesMap(str(result_triples_map.triples_map_id), str(result_triples_map.data_source), subject_map, predicate_object_maps_list, ref_form=str(result_triples_map.ref_form), iterator=str(result_triples_map.iterator), tablename=str(result_triples_map.tablename), query=str(result_triples_map.query),function=False)
		triples_map_list += [current_triples_map]
