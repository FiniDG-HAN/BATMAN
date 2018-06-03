# -*- coding: utf-8 -*-
"""
Created on Sun Jun  3 14:15:21 2018

@author: Thijs Weenink

Version: 1.0
"""
import json
import itertools


def merge_relations(dirs, file_type, the_other_file_names):
    syn_dict = _load_json("final_version/synonym_%s.txt" % (the_other_file_names.strip("__pycache__")))
    
    
    linkterm_dict = {}
    syn_dict_for_loop = {}
    
    for term in syn_dict.keys():
        cur_dict = {}
        cur_dict[term] = syn_dict.get(term)
        linkDict = _relations(term, linkterm_dict, cur_dict, syn_dict_for_loop)
        syn_dict_for_loop = _merge_dict(syn_dict_for_loop, cur_dict)
        _save_json(linkDict, "cache/linkDict.txt")

    final_relations = _clean_up(linkDict)
    return final_relations
    #_save_json(final_relations, "final_version/relations_"+the_other_file_names)
    
 

"""
#
# Comparing the pmids from terms, returns the "relationterm" dictionary
#
"""
def _relations(search_term, linkterm_dict, synonym_dict_current, synonym_dict_previous):
    previous_terms = synonym_dict_previous.keys()
    future_dict_keys = [item for item in itertools.chain(previous_terms, [search_term])]
    all_terms_pmid_dict = _merge_dict(synonym_dict_current, synonym_dict_previous)

    relation_term = {}

    for term_key in future_dict_keys:
        key_apostrophe_s_pmids_set = set((all_terms_pmid_dict.get(term_key)[1]).keys())
        link_term = {}
        for term_value in future_dict_keys:
            if term_key == term_value or (term_value in term_key.split()):
                continue
            else:
                value_apostrophe_s_pmids_set = set((all_terms_pmid_dict.get(term_value)[1]).keys())
                intersected = key_apostrophe_s_pmids_set.intersection(value_apostrophe_s_pmids_set)
                link_term[term_value] = [ item for item in intersected]

        relation_term[term_key] = link_term

    return relation_term  
 
"""
#
# Removes spaces and empty values
#
"""    
def _clean_up(dictionary):
    relations_dict = {}
    
    for key, int_dict in dictionary.items(): 
        new_dict = {k:v for k,v in int_dict.items() if v} #((not key.strip() in (k.split()) and not k.strip() in key.split()) and v)}
        relations_dict[key] = new_dict   

    
    #for key, dict_itn in relations_dict.items():
        #print(key+": "+str(dict_itn)+"\n")
    return relations_dict   
    
    
def _merge_dict(*dict_list):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_list:
        result.update(dictionary)
    return result    
    
    
    
def _load_json(file_path):
    with open("%s" % (file_path)) as file:
        data = json.load(file)
    file.close()
    return data
    
   
    
def _save_json(dictionary, name):
    with open("%s" % (name), "w") as file:
        json.dump(dictionary, file)
    file.close()