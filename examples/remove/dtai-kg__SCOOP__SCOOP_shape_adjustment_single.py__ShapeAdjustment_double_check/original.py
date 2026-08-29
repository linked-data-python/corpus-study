# Extracted from dtai-kg/SCOOP@40c6fc0420 : SCOOP/shape_adjustment_single.py
# region: ShapeAdjustment.double_check (lines 596-602, stratum remove)
# licence of the source repository: see meta.json
def double_check(self):
    double_check_list = [self.shaclNS.datatype, self.shaclNS["in"], self.shaclNS.languageIn, self.shaclNS.minCount, self.shaclNS.maxCount, self.shaclNS.minLength, self.shaclNS.maxLength, self.shaclNS.maxExclusive, self.shaclNS.minExclusive, self.shaclNS.maxInclusive, self.shaclNS.minInclusive, self.shaclNS.pattern, self.shaclNS.uniqueLang]
    for identifier in self.adjusted_identifier:
        if "NodeShape" in identifier:
            for s, p, o in self.adjusted_graph.triples((identifier, None, None)):
                if p in double_check_list:
                    self.adjusted_graph.remove((s,p,o))
