# Context shim (see meta.json): the two bindings dataset_preparation imports
# from mariocosenza/kgsum@320b14fc57 src/util.py, copied verbatim (CATEGORIES,
# match_file_lod and the two regexes it uses).  The rest of util.py is dropped
# because it loads src/filter/filter.json at import time.
# Identical for both representations.
import hashlib
import re

FILE_NUM_REGEX = re.compile(r'^(\d+)[^.]*\.(?:rdf|nt|ttl|nq)$', re.IGNORECASE)
FILE_STRING_REGEX = re.compile(r'-(.*)\.')

CATEGORIES = {
    'cross_domain', 'geography', 'government', 'life_sciences',
    'linguistics', 'media', 'publications', 'social_networking', 'user_generated'
}


def match_file_lod(file, limit, offset, lod_frame) -> int | None:
    match = FILE_NUM_REGEX.match(file)
    if not match:
        return None
    file_num = int(match.group(1))
    if file_num < offset or file_num > limit:
        return None

    match = FILE_STRING_REGEX.search(file)
    num = -1
    if match:
        extracted_string = match.group(1)
        for index, id_frame in enumerate(lod_frame['id']):
            if extracted_string == hashlib.sha256(id_frame.encode()).hexdigest():
                num = index
                return num
    if num == -1:
        return None
    return None
