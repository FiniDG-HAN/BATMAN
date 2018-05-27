# -*- coding: utf-8 -*-
"""
Created on Sun May 27 22:16:09 2018

@author: thijs
"""
import json


def clean_up_dictionary(file_name):
    dictionary = load_dict(file_name)
    processed_dict = cleans_up(dictionary)
    save_dict(file_name, processed_dict)


"""
#
# Cleans up the dictionary by removing the empty lists
#
"""
def cleans_up(dictionary):
    relations_dict = {}

    for key, int_dict in dictionary.items():
        new_dict = {k:v for k,v in int_dict.items() if v}
        relations_dict[key] = new_dict

    return relations_dict


"""
#
# File functions
#
"""
def load_dict(file_name):
    with open(file_name) as file:
        data = json.load(file)
    file.close()
    return data


def save_dict(file_name, dictionary):
    with open("processed_%s" % (file_name), "w") as output_file:
        json.dump(dictionary, output_file)
    output_file.close()
