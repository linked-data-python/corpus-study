# Extracted from tetherless-world/materialsmine@0be55da099 : tests/ingest_tester.py
# region: autoparse (lines 232-233, stratum coercion_datatype)
# licence of the source repository: see meta.json
import rdflib

expected_data["viscoelastic_measurement_mode"] = [rdflib.Literal(elem.text)
                                for elem in root.iter(".//Viscoelastic//MeasurementMode")]
