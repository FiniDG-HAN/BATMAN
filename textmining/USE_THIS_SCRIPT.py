# -*- coding: utf-8 -*-
"""
Created on Thu May 31 13:54:08 2018

Function for calling the text mining script, select a list of words from
"search_lists.py". Dont edit other files unless needed.

Author: Thijs Weenink

Version 1.0

"""

import textmining
import search_lists


def main():
    # Select a list of searchterms here
    search_list = search_lists.__search_list_test2
    # Give your list a name so you can find it later
    search_name = "search_list_temp2"
    print(search_list)

    # DONT TOUCH THIS
    textmining.main(search_list, search_name)


main()


def test():
    li = [1,2,3,4,5,6,""]
    print(li[-2:][0])
    print(str(li[-2:][0]).isnumeric())
