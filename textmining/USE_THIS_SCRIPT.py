# -*- coding: utf-8 -*-
"""
Created on Thu May 31 13:54:08 2018

Function for calling the text mining script, select a list of words from
"search_lists.py". Dont edit other files unless needed.

Author: Thijs Weenink

Known bugs: None

Version 1.0

"""

import textmining
import search_lists

"""
#
# Main function to select a list to search and perform the text mining over.
#
"""
def main():
    # Select a list of searchterms here
    search_list = search_lists.__search_list_test2
    # Give your list a name so you can find it later,
    # preferably the same name as the list you choose.
    search_name = "search_list_temp2"
    print(search_list)

    # DONT TOUCH THIS, THIS CALLS THE TEXT MINING SCRIPT
    textmining.main(search_list, search_name)


"""
#
# Calls the script
#
"""
if __name__ == "__main__":
    main()
