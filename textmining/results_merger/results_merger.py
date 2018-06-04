# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 13:35:15 2018

Processes the results stored in differend dirs as the text mining was done on
multiple computers. This script isn't fast.

Author: Thijs Weenink

Version: 1.1

Known bugs: None
"""

import json
import os
import errno

from relations_merger import *


"""
#
# Main function calling all the functions needed to process the data
#
"""
def main():
    _make_dirs()
    files = ["pmid", "processed_relations", "processed_synonym"]
    dirs = _to_merge_dirs()
    name = "".join(dirs)

    final_pmid = _merge_pmid_syn_dicts(dirs, files[0])
    final_syn = _merge_pmid_syn_dicts(dirs, files[2])

    _save_json(final_pmid, "pmid_"+name)
    _save_json(final_syn, "synonym_"+name)

    # This NEEDS to be after the others because it uses synonym file
    final_relations = merge_relations(dirs, files[1], name)
    _save_json(final_relations, "relations_"+name)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    print("Results in: %s%s%s" % (dir_path, os.sep, "final_version"))

def _merge_pmid_syn_dicts(dirs, file_type):
    mergeable_dicts = []
    for dir_to_merge in dirs:
        file_path = "%s/%s.txt" % (dir_to_merge, file_type)
        dictionary = _load_json(file_path)
        mergeable_dicts.append(dictionary)
    return _merge_dict(mergeable_dicts)

"""
#
# Combining dictionaries into 1
#
"""
def _merge_dict(dict_list):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_list:
        result.update(dictionary)
    return result


"""
#
# Make the output dirs
#
"""
def _make_dirs():
    try:
        os.mkdir("final_version")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

    try:
        os.mkdir("cache")
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


"""
#
# Load a json file to dict
#
"""
def _load_json(file_path):
    with open("%s" % (file_path)) as file:
        data = json.load(file)
    file.close()
    return data


"""
#
# Save a dict to json
#
"""
def _save_json(dictionary, name):
    with open("final_version/%s.txt" % (name), "w") as file:
        json.dump(dictionary, file)
    file.close()


"""
#
# Calling the script
#
"""
if __name__ == "__main__":
    main()
