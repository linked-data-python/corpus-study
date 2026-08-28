# Extracted from ktbs/ktbs@4f9f50c770 : utest/test_rdfrest_utils_prefix_conjunctive_view.py
# region: TestDefaultStore.teardown_method (lines 51-55, stratum remove)
# licence of the source repository: see meta.json
def teardown_method(self):
    self.g1.remove((None, None, None))
    self.g2.remove((None, None, None))
    self.ga.remove((None, None, None))
    self.gb.remove((None, None, None))
