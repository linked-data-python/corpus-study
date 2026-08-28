# Context shim (see meta.json): find_tags_from_list / find_comments_from_lists
# are HTTP clients for the LOV (Linked Open Vocabularies) API in
# mariocosenza/kgsum@320b14fc57 src/lov_data_preparation.py.  They are stubbed
# out here -- offline, deterministic, and returning what the upstream error
# path returns ([]) -- so that the Config.QUERY_LOV branch of
# process_file_full_inplace is still taken without touching the network.
# Identical for both representations.
from typing import List


def find_tags_from_list(voc_list: List[str]) -> List[str]:
    return []


def find_comments_from_lists(curi_list: List[str], puri_list: List[str]) -> List[str]:
    return []
