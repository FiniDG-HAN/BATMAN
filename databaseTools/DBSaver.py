#################################
# Methodes om gegevens van de   #
# textmining op te slaan in     #
# de databank.                  #
#################################
# Gemaakt door: Alex Janse      #
# Versie 2.0.0.                 #
# Datum: 25-05-2018             #
#################################

import DBConnector as dbc                               # wordt gebruikt om de cursor en de connectie object op te halen
import DBLoader as dbl
import traceback                                        # Wordt gebruikt om de volledige error te krijgen ipv alleen de titel
# from flask import Flask

# app = Flask(__name__, instance_relative_config=True)

# todo: exception handeling
# Hoofd methode die de sub methodes aanroept om de verschillende directories op te slaan
def save(synonymDict, pmidDict, linkDict):
    try:
        cursor, connection = dbc.connect()              # De cursor en connection objecten worden op gehaald om queries te kunnen uitvoeren en de verbinding te verbreken
        savePMID(pmidDict,cursor)                       # De savePMID wordt aangeroepen om de gegevens van de pmidDict op te slaan in de db
        saveTerms(synonymDict, cursor)
        saveLinks(linkDict,cursor)
        commit(cursor)                                  # De commit methode wordt aangeroepen als er geen exceptions zijn geweest en de queries die zijn uitgevoerd bevestigd kunnen worden in de db
        connection.disconnect()                         # Verbreek de connectie met de db
        dbl.getData()                                   # maak van de db een JSON
    except Exception as e:
        print(str(traceback.format_exc()))              # Laat de error zien als deze heeft plaats gevonden

# Methode om de gegevens uit de dictonary te halen
# en de methodes aan te roepen die ze vervolgens op slaat
def saveTerms(dict, cursor):
    for mainterm in dict.keys():
        valueList = dict[mainterm]                      # Bevat [[synonymen],[pmid],category]
        category = valueList[2]
        pmid = valueList[1]
        synonymList = valueList[0]
        saveCategory(category, cursor)
        saveMainTerm(mainterm,category,cursor)
        saveTermPMID(pmid,mainterm,cursor)
        for synonym in synonymList:
            saveSynonym(synonym,mainterm,cursor)

# Methode om de category op te slaan als deze nog niet in de db staat
def saveCategory(category, cursor):
    if checkUniqueness("type","classification",category,cursor):
        cursor.execute("INSERT INTO type VALUES (%s)", (category,))

def saveMainTerm(term,category,cursor):
    if checkUniqueness("node","mainterm",term,cursor):
        cursor.execute("INSERT INTO node VALUES (%s,%s)",(term,category))
        return False
    return True

def saveTermPMID(pmidDict,term,cursor):
    for pmid in pmidDict.keys():
        score = pmidDict[pmid]
        if checkUniqueness("nodeXarticle","mainterm",term,cursor," AND pmid LIKE \""+pmid+"\""):
            cursor.execute("INSERT INTO nodeXarticle VALUES (%s,%s,%s)",(term,pmid,score))

def checkUniqueness(tableName,columnName,
                    searchTerm,cursor,extraSQL = ""):
    query = "SELECT "+columnName+" FROM "+tableName+" WHERE "+columnName+" LIKE %s"
    if extraSQL != "":
        query += extraSQL
    cursor.execute(query,(searchTerm,))
    count = 0
    for resultaat in cursor:
        count += 1
    if count > 0:
        return False
    else:
        return True

def saveSynonym(synonym,mainterm,cursor):
    if checkUniqueness("keyword","word",synonym,cursor," AND mainterm LIKE \""+mainterm+"\""):
        cursor.execute("INSERT INTO keyword VALUES (default,%s,%s)",(synonym,mainterm))

def commit(cursor):
    cursor.execute("COMMIT")

def savePMID(dict,cursor):
    for id in dict.keys():
        if checkUniqueness("pubmed_article","pmid",id,cursor):
            data = dict[id]
            cursor.execute("INSERT INTO pubmed_article VALUES (%s,%s,%s,%s)",
                           (id,data[0],data[1],data[2]))

def saveLinks(dict,cursor):
    for term in dict.keys():
        linkTermDict = dict[term]
        for linkterm in linkTermDict.keys():
            pmidList = linkTermDict[linkterm]
            linkID = getLinkID(cursor)
            score = getTotalScore(term,linkterm,pmidList,cursor)
            cursor.execute("INSERT INTO link VALUES (%s,%s)",(linkID,score))
            insertNodeLink(term,linkID,cursor)
            insertNodeLink(linkterm,linkID,cursor)

def getLinkID(cursor):
    cursor.execute("SELECT link_id FROM link")
    row = cursor.fetchone()
    maxID = 0
    while row is not None:
        if int(row[0]) > maxID:
            maxID = int(row[0])
        row = cursor.fetchone()
    maxID += 1
    return maxID

def insertNodeLink(term,linkID,cursor):
    cursor.execute("INSERT INTO nodeXlink VALUES (%s,%s)", (linkID, term))

def getTotalScore(term,linkterm,pmidList, cursor):
    totalScore = 0
    for pmid in pmidList:
        totalScore += (getScore(term,pmid,cursor) + getScore(linkterm,pmid,cursor))
    return totalScore

def getScore(term,pmid,cursor):
    cursor.execute("SELECT score FROM nodeXarticle WHERE mainterm LIKE %s AND pmid LIKE %s",(term,pmid))
    score = 0
    for foundScore in cursor:
        score = int(foundScore[0])
    return score

# @app.route("/")
# def test():
#     return save({"testTerm":[["ts2"],{"pmidtest":5},"test33"],"testTerm2":[["ts4"],{"pmidtest":6},"test33"]}
#                 ,{"pmidtest":["titeltest","authortest",19950803]},
#                 {"testTerm":{"testTerm2":["pmidtest"]}})
#
# if __name__ == '__main__':
#     app.run(debug=True)