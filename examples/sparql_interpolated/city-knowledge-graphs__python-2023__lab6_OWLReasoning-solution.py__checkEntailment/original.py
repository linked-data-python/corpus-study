# Extracted from city-knowledge-graphs/python-2023@eadf6f94a9 : lab6/OWLReasoning-solution.py
# region: checkEntailment (lines 48-56, stratum sparql_interpolated)
# licence of the source repository: see meta.json
def checkEntailment(g, triple):

    #We use an ASK query instead of a select. It could be done with SELETCT and then checking that the results are not empty 
    qres = g.query(
    """ASK {""" + triple + """ }""")

    #Single row with one boolean vale
    for row in qres:
        print("Does '" + triple + "' hold? " + str(row))
