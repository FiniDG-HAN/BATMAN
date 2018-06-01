# -*- coding: utf-8 -*-
"""
Created on Sun May 27 22:16:09 2018

@author: Thijs Weenink

Processing of the textmining files.

Version: 1.2
"""
import json
import os


def clean_up_data_relation_dict(dictionary, file_name):
    #first_proc_dict = first_clean_up(dictionary)
    processed_dict = _clean_up(dictionary)
    final_dict = _delete_carbohydrates_from_dict(processed_dict)
    file_string = "cache%sprocessed_%s" % (os.sep, file_name)
    _save_dict(file_string, final_dict) 
    return file_string


def clean_up_data_other_dicts(dictionary, file_name, search_list_name):
    final_dict = _delete_carbohydrates_from_dict(dictionary)
    print("final dict")
    print(final_dict)
    print("###")
    if not file_name == "pmid":
        file_string = "cache%sprocessed_%s" % (os.sep, file_name)
    else:
        file_string = "results%s%s%s%s" % (os.sep, search_list_name, os.sep, file_name)
    _save_dict(file_string, final_dict)
    return file_string
    
    
    
"""
#
# Deletes the "carbohydrates" key from the dictionary if present
#
""" 
def _delete_carbohydrates_from_dict(dictionary):
    if "carbohydrates" in dictionary: del dictionary["carbohydrates"] 
    return dictionary
        
"""
#
# Cleans up the dictionary by removing the empty lists
# 
"""
def _first_clean_up(dictionary):
    new_dict = {}
    #print(dictionary)
    
    for key, int_dict in dictionary.items(): 
        new_dict = {k:v for k,v in int_dict.items() if v}
        new_dict[key] = new_dict   
     
    #print(new_dict)
    return new_dict
 
    
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
    
    
################################################
#                                              #
# Removing pmid and links if they have 0 score #
#                                              #
################################################

def remove_zero_values(synonym_dict_file, link_dict_file, search_list_name):
    synonym = _load_json(synonym_dict_file)
    link = _load_json(link_dict_file)
    
    new_synonym, removed_synonym = _remove_zero_synonym(synonym)
    new_link = _remove_zero_link_dict(link, removed_synonym)
    synonym_path = "results%s%s%s%s" % (os.sep, search_list_name, os.sep, synonym_dict_file.strip(os.sep+"cache"))
    link_path = "results%s%s%s%s" % (os.sep, search_list_name, os.sep, link_dict_file.strip(os.sep+"cache"))
    _save_dict(synonym_path, new_synonym)
    _save_dict(link_path, new_link)
    
    return synonym_path, link_path
    

def _remove_zero_synonym(synonym):
    
    new_synonym = {}
    removed_synonym = {}
    
    for key, value in synonym.items():
        pmid_score = value[1]
        fixed_pmid_score = {k:v for k,v in pmid_score.items() if v > 0}
        removed_pmid_score = {k:v for k,v in pmid_score.items() if v == 0}
        new_synonym[key] = [value[0], fixed_pmid_score, value[2]]
        removed_synonym[key] = list(removed_pmid_score.keys())
    
    
    return new_synonym, removed_synonym
    

def _remove_zero_link_dict(link_dict, removed_synonym):
    #print(link_dict)
    updated_dict = {}
    
    for key, int_dict in link_dict.items():
        try:
            new_dict = {k:list(set(v).difference(set(removed_synonym.get(k)))) for k,v in int_dict.items()}
            if len(new_dict) > 0: updated_dict[key] = new_dict
        except TypeError:
            continue
    
    final_dict = _clean_up(updated_dict)
    return final_dict

    
def _load_json(file_name):
    with open("%s.txt" % (file_name)) as file:
        data = json.load(file)
    file.close()
    return data


"""
#
# File function for saving the dict to a json
#
"""    
def _save_dict(file_name, dictionary):
    print("save dict")
    print(dictionary)
    print("****")
    with open("%s.txt" % (file_name), "w") as output_file:
        json.dump(dictionary, output_file)
    output_file.close()


















    
    
    