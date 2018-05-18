# -*- coding: utf-8 -*-
"""
Created on Thu May 17 14:07:53 2018

@author: thijs

##############################################################
#                                                            #
# Output:                                                    #
# {hoofdterm : [[synoniemen], {pmid : score}, categorie]}    #
#                                                            #
# {PMID : [title, authors, date]}                            #
# {relationterm : {linkterm : [PMID]}                        #
#                                                            #
##############################################################




"""
from Bio import Medline
from Bio import Entrez
Entrez.email = "youi.xentoo@gmail.com"

from urllib.error import HTTPError
import time
import json
import re

import matplotlib.pyplot as plt

def main():
    """
    #
    # Outputs: PMID, mainterm, relation_term
    #
    """
    
    #search_term = "yam" 
    #search_term = "bitter gourd"
    search_terms = ["yam","diabetes"]
    for search_term in search_terms:
        PMID, mainterm, terms ,time_dict = search_ncbi(search_term)
        #print(PMID)
        #print(synterm)
        #print(mainterm)
        write_to_json(PMID, mainterm, search_term)
        
        #plot(time_dict)
        print("Sleeping 15 seconds...")
        time.sleep(15)
    
    
    PMID_search_term_data, PMID_link_term_data = load_json(search_terms[0], search_terms[1])
    relation_term = compare_two_search_word(search_terms[0], search_terms[1], PMID_search_term_data, PMID_link_term_data)
    
    #time.sleep(15) # Time-out for requests
"""
#
# Comparing
#
"""

def compare_two_search_word(search_term, link_term, PMID_search_term_data, PMID_link_term_data):
    # {relationterm : {linkterm : [PMID]} 
    relation_term = {}
    link_term_dict = {}
    
    search_term_set = set(PMID_search_term_data.keys())
    link_term_set = set(PMID_link_term_data.keys())
    intersection_set = search_term_set.intersection(link_term_set) 
    
    print("-"*40)
    print(intersection_set)
    print("-"*40)
    
    link_term_dict[link_term] = list(intersection_set)
    relation_term[search_term] = link_term_dict
    
    return relation_term


def load_json(search_term, link_term):
    with open("PMID5_%s.txt" % (search_term)) as file_search:
        PMID_search_term_data = json.load(file_search)
    file_search.close()
    
    with open("PMID5_%s.txt" % (link_term)) as file_link:
        PMID_link_term_data = json.load(file_link)
    file_link.close()
        
    return PMID_search_term_data, PMID_link_term_data

def load_csv(search_term):
    health_set = set([3,5])
    

"""
#
# Searching NCBI
#
"""
def search_ncbi(search_term):
    ##### Config #####
    max_amount_downloaded = 20
    max_return = 3
    max_number_of_attempts = 3
    title_weigth = 2
    abstract_weigth = 1
    ##################
    
    time_dict = {}
    
    PMID_data = {}
    
    PMID_score = {}
    
    relationterm = {}
    linkterm = {}
    
    #search_string = (search_term.lower())+"[TIAB] AND hasabstract[All Fields] NOT pubmed books[filter]"
    search_string = "(%s[ALL]) AND %s[TIAB] AND hasabstract[All Fields] NOT pubmed books[filter]" % (search_term.lower(), search_term.lower()) #(diabetes[ALL]) AND diabetes[TIAB] 
    record = Entrez.read(Entrez.esearch(db="pubmed", 
                            term=search_string, 
                            usehistory="y"))
    
    amount_of_hits = int(record["Count"])
    try:
        translationSet = record["TranslationSet"][0]["To"]
        terms = set(re.findall('"(.*?)"', translationSet))
    except IndexError as err:
        terms = set([search_term.lower()])
    print(terms)
    
    aprox_time = int((amount_of_hits)/60)
    aprox_hours = int(aprox_time/60)
    print("%i results found, this will take aprox. %i minutes (%i hours)" % (amount_of_hits, aprox_time, aprox_hours))
    #print(record)
    
    
    current_result = 1
    #out_handle = open("text_mining_record.txt", "w")
    time_dict[0] = 0
    start_time = time.time()
    for start in range(0,amount_of_hits,max_return): # amount_of_hits,max_return
        if start % 30:
            time.sleep(5)
        #print(start)
        #end = min(amount_of_hits, start+max_return)
        print("Downloading %i out of %i" % (current_result, amount_of_hits))
        attempt = 1
        fetched = False
        while attempt <= max_number_of_attempts and fetched == False:
            connection = True
            try:
                fetch_handle = Entrez.efetch(db="pubmed",rettype="medline",
                                             retmode="text",retstart=start,
                                             retmax=max_return,
                                             webenv=record["WebEnv"],
                                             query_key=record["QueryKey"]) 
                if connection:    
                    fetched = True
                    current_result += 1
                    
                    records = Medline.parse(fetch_handle)
                    
                    for article in records:
                        #for key in article.keys():
                         #   out_handle.write(key+": "+str(article.get(key))+"\n")
                        pmid = article["PMID"]
                        title = str(article["TI"])
                        authors = ", ".join((article["AU"])).strip("[").strip("]")
                        publish_data = str(article["DP"])
                        PMID_data[pmid] = [title, authors, publish_data]
                        
                        abstract = (article["AB"].replace("This article is protected by copyright. All rights reserved.", "")).lower()
                        
                        for syn_search_term in terms:
                            syn_ti_score = (title.count(syn_search_term))*title_weigth
                            syn_ab_score = (abstract.count(syn_search_term))*abstract_weigth
                            pmid_syn_score = syn_ti_score+syn_ab_score
                            
                            if pmid in PMID_score.keys():
                                PMID_score[pmid] += pmid_syn_score
                            else:
                                PMID_score[pmid] = pmid_syn_score
                            
                    
                          
                        
                    #abstract_search_count = abstract.count(search_term)
                    #title_search_count = title.count(search_term)
                    #score_maybe = title_search_count+abstract_search_count
                    
                    # {"bitter gourd": [["bitter gourd", "bitter", "momordica charantia"], {27190792 : 30, 27190756 : 90}, categorie]
                    
                    """
                    print("-"*40)
                    print(pmid)
                    print(title)
                    #print(abstract)
                    print("-"*40)
                    print(title_search_count)
                    print(abstract_search_count)
                    print(score_maybe)
                    """
                 
                    
                    
                    #print("-"*40)
                    #print("PMID: "+str(pmid)+"\nTitle: "+str(title)+"\nAuthors: "+str(authors)+"\nDate: "+str(publish_data))
                    #print("-"*40)
                    
                    """ 
                    data = fetch_handle.read()
                    fetch_handle.close()
                    out_handle.write(data)   """
                    
                    
            except HTTPError as err:
                if 500 <= err.code <= 599:
                    print("Received error from server %s" % err)
                    print("Attempt %i of %i" % (attempt, max_number_of_attempts))
                    attempt += 1
                    connection = False
                    time.sleep(15)
                else:
                    connection = False
                    raise
                    
                    
                    
        time_dict[current_result] = ((time.time()-start_time))  
        if current_result == (max_amount_downloaded+1):
            break
    
    mainterm = main_term_dict(terms, search_term, PMID_score)
    
    end_time = time.time()
    total_time = end_time-start_time
    print("\nTotal time elapsed: "+str(total_time))
    #out_handle.close()

    return PMID_data, mainterm, terms, time_dict
 
    
def main_term_dict(terms, search_term, PMID_score):
    mainterm = {}
    synterm = {}
    mainterm_internal_list = []
    
    mainterm_internal_list.append(list(terms)) 
                
    for key,item in PMID_score.items():
        #print(key,item)
        synterm[key] = item
    
    mainterm_internal_list.append(synterm)
    mainterm_internal_list.append(get_category(search_term))
    mainterm[search_term] = mainterm_internal_list

    return mainterm    


def get_category(search_term):
    category = "plant"
    return category


"""
#
# Plotting 
#
"""    


def plot(time_dict):
    #download, time = zip(sorted(time_dict.items()))
    
    plt.plot(*zip(*sorted(time_dict.items())))    
    plt.xlabel('Downloaded articles')
    plt.ylabel('time (s)')
    plt.title('Downloaded articles vs time')
    plt.show()

"""
    idlist = record["IdList"]
    search_results[search_term] = idlist
    return search_results
"""
    
def write_to_json(PMID, mainterm, search_term):
    with open("PMID5_%s.txt" % (search_term), "w") as output_file_PMID:
        json.dump(PMID, output_file_PMID)
    output_file_PMID.close()
    
    with open("mainterm5_%s.txt" % (search_term), "w") as output_file_mainterm:
        json.dump(mainterm, output_file_mainterm)
    output_file_mainterm.close()
    

if __name__ == "__main__":
    main()

"""
from Bio import Entrez
import time
try:
    from urllib.error import HTTPError  # for Python 3
except ImportError:
    from urllib2 import HTTPError  # for Python 2
Entrez.email = "history.user@example.com"
search_results = Entrez.read(Entrez.esearch(db="pubmed",
                                            term="Opuntia[ORGN]",
                                            reldate=365, datetype="pdat",
                                            usehistory="y"))
count = int(search_results["Count"])
print("Found %i results" % count)

batch_size = 10
out_handle = open("recent_orchid_papers.txt", "w")
for start in range(0,count,batch_size):
    end = min(count, start+batch_size)
    print("Going to download record %i to %i" % (start+1, end))
    attempt = 1
    while attempt <= 3:
        try:
            fetch_handle = Entrez.efetch(db="pubmed",rettype="medline",
                                         retmode="text",retstart=start,
                                         retmax=batch_size,
                                         webenv=search_results["WebEnv"],
                                         query_key=search_results["QueryKey"])
        except HTTPError as err:
            if 500 <= err.code <= 599:
                print("Received error from server %s" % err)
                print("Attempt %i of 3" % attempt)
                attempt += 1
                time.sleep(15)
            else:
                raise
    data = fetch_handle.read()
    fetch_handle.close()
    out_handle.write(data)
out_handle.close()


At the time of writing, this gave 28 matches - but because this is a date dependent search, this will of course vary. 
As described in Section 9.12.1 above, you can then use Bio.Medline to parse the saved records.



"""