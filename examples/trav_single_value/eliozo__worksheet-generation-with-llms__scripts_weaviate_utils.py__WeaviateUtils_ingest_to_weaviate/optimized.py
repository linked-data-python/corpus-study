# Extracted from eliozo/worksheet-generation-with-llms@c065efff55 : scripts/weaviate_utils.py
# region: WeaviateUtils.ingest_to_weaviate (lines 146-230, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, URIRef, Namespace, RDF
import sys

def ingest_to_weaviate(self, filename):
    print(f'Importing {filename} to  Weaviate')
    graph = Graph().parse(filename, format="ttl")

    if not self.client.is_ready():
        print('Weaviate client is not ready!')
        sys.exit(1)

    problemCount = 0
    for subj in graph.subjects(RDF.type, self.eliozoNS.Problem):
        try:
            val = graph.value(subj, self.eliozoNS.problemID)
            problemID = str(val)
        except Exception:
            print(f"Error converting problemID={val} for {problemCount}; skipping insert")
            continue
        problemCount += 1
        print(f'Ingesting {problemID}...')
        # Extract properties that don't require language specification
        # Initialize the data object with non-language properties
        data_object = {"problemID": problemID}
        for name, convert in (("olympiadType", str), ("problemGrade", int), ("problemYear", int)):
            try:
                val = graph.value(subj, self.eliozoNS[name])
                data_object[name] = convert(val)
            except Exception:
                print(f"Error converting {name}={val} for {problemCount}; skipping insert")
                break
        else:
            lang = 'lv'
            for obj in graph.objects(subj, self.eliozoNS.problemText):
                if obj.language == lang:
                    data_object[f"problemText_{lang}"] = str(obj)
            solution_texts = [str(solution_text) for solution_text in graph.objects(
                subj, self.eliozoNS.problemSolution / self.eliozoNS.solutionText)
                              if solution_text.language == lang]
            if solution_texts:
                data_object[f"solutionText_{lang}"] = '\n\n'.join(solution_texts)

            if not self.skipping_mode:
                self.client.collections.get("Problem").data.insert(
                    properties=data_object, references={})
    return 0, {'keyMM':'ingest_to_weaviate'}
