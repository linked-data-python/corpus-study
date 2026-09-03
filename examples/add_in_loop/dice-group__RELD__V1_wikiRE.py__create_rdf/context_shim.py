# Context shim (see meta.json): nyt, relation and rel_data -- defined
# earlier in the same function, dice-group/RELD@7ca93acbb6 V1/wikiRE.py's
# create_rdf() (relation = res+"R-"+str(ID) around line 133; rel_data =
# pd.read_csv("data/AllRelationWithCrossCheck.csv") at line 108; nyt =
# rel_data.loc[rel_data['WikidataIds'] == rel, 'RE-NYT-Relation'].iloc[0]
# at line 191) -- just outside this region's extracted line range
# (193-198), inside a `for i, (rel, info) in enumerate(output.items()):`
# loop this region does not otherwise depend on.
#
# rel_data is reproduced here with two real rows copied verbatim from the
# repository's own AllRelationWithCrossCheck.csv (repo root, not committed
# under V1/ where the script expects it): WikidataIds=P19 ("place of
# birth"), the row this region's nyt/relation values below exercise, plus
# a neighbour row (P569, "date of birth") whose RE-NYT-Relation is blank
# in the real file, so the .loc[...] filter is not trivially the whole
# table. relation is res+"R-"+str(Wrid) for the P19 row (Wrid=5001).
# Identical for both representations.
import pandas as pd

rel_data = pd.DataFrame([
    {"WikidataIds": "P569", "Wrid": 5000, "RE-WikiRE-Relation": "date of birth",
     "Nrid": 4000, "RE-NYT-Relation": float("nan")},
    {"WikidataIds": "P19", "Wrid": 5001, "RE-WikiRE-Relation": "place of birth",
     "Nrid": 4001, "RE-NYT-Relation": "place_of_birth"},
])

relation = "https://reld.dice-research.org/resource/R-5001"
nyt = "place_of_birth"
