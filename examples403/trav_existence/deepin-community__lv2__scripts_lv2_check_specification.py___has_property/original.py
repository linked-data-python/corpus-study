# Extracted from deepin-community/lv2@1240cf5811 : scripts/lv2_check_specification.py
# region: _has_property (lines 72-75, stratum trav_existence)
# licence of the source repository: see meta.json
def _has_property(model, subject, predicate):
    "Return true if subject has any value for predicate in model."

    return model.value(subject, predicate, None) is not None
