# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_adjustment_single.py
# region: ShapeAdjustment.double_check (lines 596-602, stratum remove)
# licence of the source repository: see meta.json
def double_check(self):
    double_check_list = ["datatype", "in", "languageIn", "minCount", "maxCount", "minLength",
                         "maxLength", "maxExclusive", "minExclusive", "maxInclusive",
                         "minInclusive", "pattern", "uniqueLang"]
    for identifier in self.adjusted_identifier:
        if "NodeShape" in identifier:
            for name in double_check_list:
                self.adjusted_graph.remove((identifier, self.shaclNS[name], None))
