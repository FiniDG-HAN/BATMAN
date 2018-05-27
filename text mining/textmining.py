# -*- coding: utf-8 -*-
"""
Created on Thu May 17 14:07:53 2018

Version 1.5.1

@authors: Thijs Weenink and Fini De Gruyter

##############################################################
#                                                            #
# Output:                                                    #
# {mainterm : [[synoniemen], {pmid : score}, categorie]}     #
#                                                            #
# {PMID : [title, authors, date]}                            #
# {relationterm : {linkterm : [PMID]}                        #
#                                                            #
##############################################################

"""

from Bio import Medline
from Bio import Entrez
Entrez.email = "youi.xentoo@gmail.com"

try:
    from urllib.error import HTTPError, URLError  # for Python 3
except ImportError:
    from urllib2 import HTTPError, URLError  # for Python 2

import time
import json
import csv
import re
import itertools

import matplotlib.pyplot as plt
import numpy

import afterprocessing

def main():
    """
    #
    # Outputs: PMID, mainterm, relation_term
    #
    """
    print("Start of script")
    one_of_the_terms_doesnt_give_results = False

    cat_dict = load_csv()

    pmid_dict = {}
    synonym_dict = {}
    linkterm_dict = {}

    index_test = int(get_previous_search_index())

    search_terms = list(cat_dict.keys())[int(index_test)::]
    print(search_terms)
    print(len(search_terms))

    for index_of_searches, search_term in enumerate(search_terms):
        try:
            linkterm_dict, pmid_dict, synonym_dict = get_previous_search_terms("relations", "pmid", "synonym")
        except Exception:
            make_history("relations", "pmid", "synonym")

        # Main text mining function, PMID and mainterm are dictonaries,
        # structure can be seen on line 7-15
        print("Search term: %s" % (search_term))
        PMID, synonym, terms ,time_dict = text_mining(search_term, cat_dict)

        """
        # Plotting useful with testing
        if not time_dict == None:
            plot(time_dict)
        """

        # Making sure the script doesnt continue if one of the search terms doesnt give any results
        if PMID == None or synonym == None or time_dict == None:
            one_of_the_terms_doesnt_give_results = True
            faulty_search_term = search_term


        if not one_of_the_terms_doesnt_give_results: # So if all terms have results...

            linkDict = relations(search_term, linkterm_dict, synonym, synonym_dict)

            # Combining dictionaries into 1:
            pmidDict = merge_dict(pmid_dict, PMID)
            synonymDict = merge_dict(synonym, synonym_dict)

            filenames = ["relations", "pmid", "synonym"]
            dicts = [linkDict, pmidDict, synonymDict]
            dump_to_json(dicts, filenames)


            print("finished textmining")
        else:
            print("The search term %s didn't return any results" % (faulty_search_term))

        add_to_search_indexes(str(index_of_searches + int(index_test)))

        #if index_of_searches == 4:
         #   break

    # Cleans up the dictionary as I dont want to mess with this script anymore
    afterprocessing.clean_up_dictionary("relations.txt")

"""
#
# Comparing the pmids from terms, returns the "relationterm" dictionary
#
"""
def relations(search_term, linkterm_dict, synonym_dict_current, synonym_dict_previous):
    previous_terms = synonym_dict_previous.keys()
    future_dict_keys = [item for item in itertools.chain(previous_terms, [search_term])]
    all_terms_pmid_dict = merge_dict(synonym_dict_current, synonym_dict_previous)

    relation_term = {}

    for term_key in future_dict_keys:
        key_apostrophe_s_pmids_set = set((all_terms_pmid_dict.get(term_key)[1]).keys())
        link_term = {}
        for term_value in future_dict_keys:
            if term_key == term_value:
                continue
            else:
                value_apostrophe_s_pmids_set = set((all_terms_pmid_dict.get(term_value)[1]).keys())
                intersected = key_apostrophe_s_pmids_set.intersection(value_apostrophe_s_pmids_set)
                link_term[term_value] = [ item for item in intersected]

        relation_term[term_key] = link_term

    return relation_term


"""
#
# Combining dictionaries into 1
#
"""
def merge_dict(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


"""
#
# Fuctions using files
#
"""
# Gets the previous dictionaries
def get_previous_search_terms(relation, pmid, synonym):
    with open("%s.txt" % (relation), "r") as relations_file:
        relation_dict = json.load(relations_file)
    relations_file.close()

    with open("%s.txt" % (pmid), "r") as pmid_file:
        pmid_dict = json.load(pmid_file)
    pmid_file.close()

    with open("%s.txt" % (synonym), "r") as synonym_file:
        synonym_dict = json.load(synonym_file)
    synonym_file.close()

    return relation_dict, pmid_dict, synonym_dict

def make_history(relation, pmid, synonym):
    with open("%s.txt" % (relation), "w") as relations_file:
        relations_file.close()

    with open("%s.txt" % (pmid), "w") as pmid_file:
        pmid_file.close()

    with open("%s.txt" % (synonym), "w") as synonym_file:
        synonym_file.close()

# Writes a dictionary to a JSON file
def dump_to_json(dicts, filenames):
    for index, dictionary in enumerate(dicts):
        filename = str(filenames[index])
        with open("%s.txt" % (filename), "w") as output_file:
            json.dump(dictionary, output_file)
        output_file.close()

# Loads the JSON file of the search term and the link term into dictionaries
def load_json(file_type, search_term, link_term):
    with open("%s_%s.txt" % (file_type, search_term)) as file_search:
        search_term_data = json.load(file_search)
    file_search.close()

    with open("%s_%s.txt" % (file_type, link_term)) as file_link:
        link_term_data = json.load(file_link)
    file_link.close()

    return search_term_data, link_term_data

# Loads a csv file to a dictionary, tab seperated in this case
def load_csv():
    reader = csv.DictReader(open('keywords.csv'), delimiter="\t")

    result = {}
    for row in reader:
        for column, value in row.items():
            if not value == "":
                result.setdefault(value.lower(), column)

    return result

# Specifies which category the term belongs to
def get_category(cat_dict, synterms):
    categories = []

    for term in synterms:
        cat = cat_dict.get(term)
        if not cat == None:
            categories.append(cat)

    return str(set(categories)).strip("{").strip("}").strip("'")

"""
#
# In case the script crashes or NCBI throws out the script, so you dont have to strart from the beginning again
#
"""
def get_previous_search_index():
    try:
        with open("previous_search_index.txt", "a+") as file:
            file.seek(0)
            lines = [i.strip() for i in file.readlines()]
            file.close()
    except Exception as err:
        print("Error: "+str(err))

    if len(lines) == 0:
        index = 0
    else:
        index = max(lines)+1

    return index

"""
#
# Adds an number to the indexes file
#
"""
def add_to_search_indexes(index):
    try:
        if index == 0:
            with open("previous_search_index.txt", "w") as file:
                file.write(str(0)+"\n")
                file.close()
        else:
            with open("previous_search_index.txt", "a+") as file:
                file.seek(0)
                file.write(str(index)+"\n")
                file.close()

    except Exception as err:
        print("Error: "+str(err))


"""
#
# Searching NCBI
#
"""
# The main function for text mining, with configuration file
def text_mining(search_term, cat_dict):
    ##### Config #####
    max_amount_downloaded = 500
    max_return = 5
    max_number_of_attempts = 3
    title_weigth = 2
    abstract_weigth = 1
    ##################

    max_amount_downloaded = int(max_amount_downloaded/max_return)

    terms, amount_of_hits, record = ncbi_search(search_term)
    if not record == None and amount_of_hits > 0:
        return ncbi_fetch(record, search_term, terms, amount_of_hits,
                          [max_amount_downloaded, max_return, max_number_of_attempts, title_weigth, abstract_weigth],
                          cat_dict)
    else:
        return None, None, terms, None


# Searches the PubMed database with the search term, returns the TranslationSet, amount of hits and the esearch record
def ncbi_search(search_term):

    if search_term.lower() == "momordica charantia":
        search_term = "bitter gourd"

    search_string = "(%s[ALL]) AND %s[TIAB] AND hasabstract[All Fields] NOT pubmed books[filter]" % (search_term.lower(), search_term.lower()) #(diabetes[ALL]) AND diabetes[TIAB]

    try:
        record = Entrez.read(Entrez.esearch(db="pubmed",
                                term=search_string,
                                usehistory="y"))

        amount_of_hits = int(record["Count"])
        try:
            translationSet = record["TranslationSet"][0]["To"]
            print(translationSet)
            terms = set(re.findall('"(.*?)"', translationSet))
        except IndexError as err:
            terms = set([search_term.lower()])
        except Exception as err:
            raise
    except RuntimeError as err:
        amount_of_hits = 0
        record = None

    aprox_time = int(((0.2282835*amount_of_hits)+(4.0993715))/60)
    aprox_hours = int(aprox_time/60)
    print("%i results found, this will take aprox. %i minutes (%i hours)\n" % (amount_of_hits, aprox_time, aprox_hours))
    return terms, amount_of_hits, record
    #print(record)


# Fetches the data from the record gotten from ncbi_search(), returns all data needed
def ncbi_fetch(record, search_term, terms, amount_of_hits, config, cat_dict):
    time_dict = {}

    max_amount_downloaded = config[0]
    max_return = config[1]
    max_number_of_attempts = config[2]
    title_weigth = config[3]
    abstract_weigth = config[4]

    # All of the dictionaries needed in this function
    PMID_data = {}
    PMID_score = {}

    current_result = 1
    #out_handle = open("text_mining_record.txt", "w")
    time_dict[0] = 0
    start_time = time.time()

    for start in range(0,amount_of_hits,max_return): # amount_of_hits,max_return
        if start % 60 == 0:
            time.sleep(5)

        #print("Downloading %i out of %i" % (current_result, amount_of_hits))
        end = min(amount_of_hits, start+max_return)
        print("Downloading record %i to %i" % (start+1, end))
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

            except HTTPError as err:
                if 500 <= err.code <= 599:
                    print("Received error from server %s" % err)
                    print("Attempt %i of %i" % (attempt, max_number_of_attempts))
                    attempt += 1
                    connection = False
                    time.sleep(15)
                else:
                    connection = False
                    print("NCBI doesn't want to cooperate with this download")
                    pass
            except URLError as err:
                print("Connection lost, waiting 15 seconds")
                attempt += 1
                connection = False
                time.sleep(15)
            except Exception as err:
                connection = False

            # Only performed if there is a connection
            if connection:
                fetched = True
                current_result += 1

                records = Medline.parse(fetch_handle)

                for article in records:
                    try:
                        pmid = article["PMID"]
                        title = str(article["TI"])
                        authors = ", ".join((article["AU"])).strip("[").strip("]")
                        publish_data = str(article["DP"])

                        # PMID dictionary:
                        PMID_data[pmid] = [title, authors, publish_data]

                        abstract = (article["AB"].replace("This article is protected by copyright. All rights reserved.", "")).lower()

                        # The PMID score dictionary, part of the mainterm dictionary:
                        for syn_search_term in terms:
                            syn_ti_score = (title.count(syn_search_term))*title_weigth
                            syn_ab_score = (abstract.count(syn_search_term))*abstract_weigth
                            pmid_syn_score = syn_ti_score+syn_ab_score

                            if pmid in PMID_score.keys():
                                PMID_score[pmid] += pmid_syn_score
                            else:
                                PMID_score[pmid] = pmid_syn_score
                    except KeyError as err:
                        pass
                    except Exception as err:
                        raise

            ### End of if statement ###
        if current_result >= max_amount_downloaded:
            break

        # Mostly for testing only
        time_dict[start] = ((time.time()-start_time))

    mainterm = main_term_dict(terms, search_term, PMID_score, cat_dict)

    end_time = time.time()
    total_time = end_time-start_time
    print("\nTotal time elapsed: "+str(total_time))

    return PMID_data, mainterm, terms, time_dict


"""
#
# The creation of the mainterm dictionary
#
"""
def main_term_dict(terms, search_term, PMID_score, cat_dict):
    mainterm = {}
    synterm = {}
    mainterm_internal_list = []

    mainterm_internal_list.append(list(terms))

    for key,item in PMID_score.items():
        #print(key,item)
        synterm[key] = item

    mainterm_internal_list.append(synterm)
    category = get_category(cat_dict, terms)
    if category == "set()":
        category = "none"
    mainterm_internal_list.append(category)
    mainterm[search_term] = mainterm_internal_list

    return mainterm


"""
#
# Plotting, mainly used for testing
#
"""
def plot(time_dict):
    #download, time = zip(sorted(time_dict.items()))
    try:
        x, y = zip(*sorted(time_dict.items()))
            # calc the trendline
        z = numpy.polyfit(x, y, 1)
        # the line equation:
        print("y=%.6fx+(%.6f)"%(z[0],z[1]))
    except Exception as err:
        print("zip")


    plt.plot(*zip(*sorted(time_dict.items())))
    plt.xlabel('Downloaded articles')
    plt.ylabel('time (s)')
    plt.title('Downloaded articles vs time')
    plt.show()


"""
#
# Calling the script
#
"""
if __name__ == "__main__":
    main()


###############################################################################
###############################################################################
###############################################################################

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


# Previously in ncbi_fetch(), before the "except HTTPError":
    #abstract_search_count = abstract.count(search_term)
    #title_search_count = title.count(search_term)
    #score_maybe = title_search_count+abstract_search_count

    # {"bitter gourd": [["bitter gourd", "bitter", "momordica charantia"], {27190792 : 30, 27190756 : 90}, categorie]


    print("-"*40)
    print(pmid)
    print(title)
    #print(abstract)
    print("-"*40)
    print(title_search_count)
    print(abstract_search_count)
    print(score_maybe)




    #print("-"*40)
    #print("PMID: "+str(pmid)+"\nTitle: "+str(title)+"\nAuthors: "+str(authors)+"\nDate: "+str(publish_data))
    #print("-"*40)


    data = fetch_handle.read()
    fetch_handle.close()
    out_handle.write(data)


>>> REMOVE LINES 250-253 AT FINAL RELEASE <<<





"""
