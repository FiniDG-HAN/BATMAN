#############################
# Methodes om de data       #
# uit de db te halen en     #
# op te slaan in een JSON.  #
#############################
# Gemaakt door: Alex Janse  #
# Versie: 1.0.0.            #
# Datum: 03-06-2018         #
#############################

import DBConnector as dbc
import traceback
import json
# from flask import Flask

# app = Flask(__name__, instance_relative_config=True)

# Hoofdmethode die connectie ophaald, sluit en de cursor door geeft aan de volgende methodes
def getData():
    try:
        cursor, connection = dbc.connect()          # De cursor en connection objecten worden op gehaald om queries te kunnen uitvoeren en de verbinding te verbreken
        data = __createJSONData(cursor)             # Haalt de data op vanuit de db
        __createJSON(data)                          # Maakt van de db data een JSON bestand voor de applicatie
        connection.close()
    except Exception as e:
        print(str(traceback.format_exc()))          # Laat de error zien als deze heeft plaats gevonden. Vanwege de brede scala aan SQL errors is er voor gekozen om de algemene Exception te pakken en de details te laten printen voor de developer

# Methode die van de db data maakt voor een json bestand
def __createJSONData(cursor):
    cursor.execute("SELECT * FROM node")            # Haalt alle nodes op zodat vanaf daar de gehele db kan worden door gezocht
    catDict = {}                                    # Een dict die bij houdt welke categoriën er al zijn geweest
    catMax = 0                                      # Index variable om bij te houden welke kleur getal d3 moet gebruiken
    data = dict()                                   # Dict waar alles in wordt opgeslagen
    data["nodes"] = []                              # Maak nodes key aan om de node data in op te slaan
    data["links"] = []                              # Maak links key voor de link data
    results = cursor.fetchall()                     # Sla alle resultaten op van de sql query in een variable
    linkMemory = []                                 # Houdt bij welke links er al zijn gemaakt om duplicaten te voorkomen
    for result in results:
        term = result[0]
        category = result[1]
        pmidScoreDict, nodeScore = getScorePMID(term,cursor)
        synonyms = getSynonyms(term,cursor)
        pmidDict = getPMIDData(pmidScoreDict,cursor)
        linkDict = getLink(term, cursor)
        data, catDict, catMax = __createNodes(term, category,
                                              nodeScore, synonyms,
                                              pmidDict, data,
                                              catDict, catMax)
        data, linkMemory = __createLinks(linkDict, term, data, cursor, linkMemory)
    return data

# Methode om JSON bestand te maken
def __createJSON(data):
    bestand = open(r'/home/owe8_pg8/public_html/BATMAN/static/json/test2.json','w')
    json.dump(data, bestand, indent=4, sort_keys=True, default=str)
    bestand.close()

# Methode om de nodes data op te slaan in de data dict
def __createNodes(term, category, nodeScore, synonyms, pmidDict, data, catList, catMax):
    group, catList, catMax = getCatInt(category, catList,catMax)
    data["nodes"].append({
        'id' : term,
        'group' : group,
        'nodeScore' : nodeScore,
        'synonyms' : synonyms,
        'articles' : []
    })
    index = len(data["nodes"])-1
    for pmid in pmidDict.keys():
        data["nodes"][index]["articles"].append({
            'pmid' : pmid,
            'title' : pmidDict[pmid][0],
            'authors' : pmidDict[pmid][1],
            'date' : pmidDict[pmid][2],
            'score' : pmidDict[pmid][3]
        })
    return data, catList, catMax

# Methode om de link data op te slaan in de data dict
def __createLinks(linkDict, hoofdterm, data, cursor, linkMemory):
    for linkID in linkDict.keys():
        for lijst in linkMemory:
            linkTerm = getLinkTerm(linkID, hoofdterm, cursor)
            if not (lijst.__contains__(hoofdterm) and lijst.__contains__(linkTerm)):
                data["links"].append({
                    'source' : hoofdterm,
                    'target' : linkTerm,
                    'value' : linkDict[linkID]
                })
                linkMemory.append([hoofdterm,linkTerm])

    return data,linkMemory

# Methode om de category kleur index te bepalen en te retourneren
def getCatInt(category,catList, catMax):
    if catList.keys().__contains__(category):
        return catList[category], catList, catMax
    else:
        catList[category] = catMax
        return catMax, catList, catMax+1

# Methode om de term op te halen die gelinkt is aan een hoofdterm
def getLinkTerm(linkID,hoofdTerm,cursor):
    cursor.execute("SELECT term FROM nodeXlink WHERE link_id LIKE %s AND term NOT LIKE %s",(linkID,hoofdTerm))
    term = ""
    for (result,) in cursor:
        term = result
    return term

# Methode om de scores per pmid van een term op te halen
def getScorePMID(term,cursor):
    cursor.execute("SELECT pmid, score FROM nodeXarticle WHERE mainterm LIKE %s",(term,))
    totalScore = 0
    pmidDict = {}
    for (pmid, score) in cursor:
        totalScore += int(score)
        pmidDict[pmid] = score
    return pmidDict, totalScore

# Methode om de synonymen van een term op te halen
def getSynonyms(term,cursor):
    cursor.execute("SELECT word FROM keyword WHERE mainterm LIKE %s",(term,))
    synonyms = []
    for (word,) in cursor:
        synonyms.append(word)
    return synonyms

# Methode om de data van PMID op te halen
def getPMIDData(pmidScoreDict,cursor):
    pmidDict = {}
    for pmid in pmidScoreDict.keys():
        cursor.execute("SELECT title, authors, publication_date FROM pubmed_article WHERE pmid LIKE %s",(pmid,))
        data = []
        for (titel, authorLijst, datum) in cursor:
            data.append(titel)
            data.append(authorLijst)
            data.append(datum)
            data.append(pmidScoreDict[pmid])
        pmidDict[pmid] = data
    return pmidDict

# Methode om de link id en score op te slaan
def getLink(term,cursor):
    cursor.execute("SELECT link_id FROM nodeXlink WHERE term LIKE %s",(term,))
    links = {}
    results = cursor.fetchall()
    for result in results:
        link_id = result[0]
        links[link_id] = getLinkScore(link_id,cursor)
    return links

# Methode om de link score op te halen
def getLinkScore(link,cursor):
    cursor.execute("SELECT relation_score FROM link WHERE link_id LIKE %s",(link,))
    score = 0
    for (item,) in cursor:
        score = int(item)
    return score

# @app.route("/")
# def test():
#     return getData()
#
# if __name__ == '__main__':
#     app.run(debug=True)
