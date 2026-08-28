# Extracted from JustlyAI/lmss_entity_extractor@6acc4d8389 : app/run_search.py
# region: main (lines 28-66, band low)
# licence of the source repository: see meta.json
import argparse
import logging
from context import LMSS_DIR, load_top_classes   # context shim, see meta.json
from lmss_search import LMSSSearch               # context shim, see meta.json
from rdflib import Graph
ONTOLOGY_FILE = LMSS_DIR / "LMSS.owl"
INDEX_FILE = LMSS_DIR / "lmss_index.json"
GRAPH_FILE = LMSS_DIR / "lmss_graph.ttl"
TOP_CLASSES_FILE = LMSS_DIR / "top_classes.json"
logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Search LMSS ontology")
    args = parser.parse_args()

    # Load the ontology
    ontology_graph = Graph()
    ontology_graph.parse(ONTOLOGY_FILE, format="xml")
    logger.info(f"Loaded ontology from {ONTOLOGY_FILE}")

    # Load top-level classes from JSON file
    top_level_classes = load_top_classes(TOP_CLASSES_FILE)
    logger.info(
        f"Loaded {len(top_level_classes)} top-level classes from {TOP_CLASSES_FILE}"
    )

    # Prompt user for keyword search
    keyword = input("Enter the keyword for search: ")

    # Prompt user for top classes
    top_classes_input = input(
        "Enter top classes separated by commas (or press Enter for all classes): "
    )
    if top_classes_input:
        selected_classes = [cls.strip() for cls in top_classes_input.split(",")]
    else:
        selected_classes = None

    # Perform search with selected classes
    searcher = LMSSSearch(INDEX_FILE, GRAPH_FILE, TOP_CLASSES_FILE)
    search_results = searcher.search(keyword, selected_branches=selected_classes)

    # Print search results
    print("\nSearch Results:")
    for result in search_results:
        print(
            f"- {result['label']} (IRI: {result['iri']}, Score: {result['score']:.2f})"
        )

    logger.info(f"Search results: {search_results}")


# --- demo harness (added identically to both representations; see meta.json) ---
# main() takes no arguments, returns nothing and keeps its graph in a local, so
# the only observable it offers is stdout.  argv and the two interactive
# prompts are answered deterministically here; `input` defined at module level
# shadows the builtin for main().
import sys
sys.argv = ["run_search.py"]
_answers = iter(["class", "http://example.org/ontology#ParentClass"])

def input(prompt=""):
    answer = next(_answers)
    print(prompt + answer)
    return answer

main()
