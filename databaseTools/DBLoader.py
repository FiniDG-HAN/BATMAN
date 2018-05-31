import DBConnector as dbc
import traceback
import json
from flask import Flask

app = Flask(__name__, instance_relative_config=True)

def getData():
    try:
        cursor, connection = dbc.connect()
        data = createJSONData(cursor)
        createJSON(data)
        connection.close()
        return "klaar"
    except Exception as e:
        return str(traceback.format_exc())


def createJSONData(cursor):
    cursor.execute("SELECT * FROM node")
    catList = {}
    catMax = 0
    data = {}
    data["nodes"] = []
    data["links"] = []
    results = cursor.fetchall()
    linkMemory = []                                                 # Houdt bij welke links er al zijn gemaakt om duplicaten te voorkomen
    for result in results:
        term = result[0]
        category = result[1]
        pmidScoreDict, nodeScore = getScorePMID(term,cursor)
        synonyms = getSynonyms(term,cursor)
        pmidDict = getPMIDData(pmidScoreDict,cursor)
        linkDict = getLink(term, cursor)
        data, catList, catMax = createNodes(term, category,
                                            nodeScore,synonyms,
                                            pmidDict, data,
                                            catList, catMax)
        data, linkMemory = createLinks(linkDict,term,data,cursor,linkMemory)
    return data

def createJSON(data):
    bestand = open(r'/home/owe8_pg8/public_html/BATMAN/static/json/test2.json','w')
    json.dump(data, bestand, indent=4, sort_keys=True, default=str)
    bestand.close()

def createNodes(term, category, nodeScore, synonyms, pmidDict, data, catList, catMax):
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

def createLinks(linkDict,hoofdterm,data,cursor,linkMemory):
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


def getCatInt(category,catList, catMax):
    if catList.keys().__contains__(category):
        return catList[category], catList, catMax
    else:
        catList[category] = catMax
        return catMax, catList, catMax+1

def getLinkTerm(linkID,hoofdTerm,cursor):
    cursor.execute("SELECT term FROM nodeXlink WHERE link_id LIKE %s AND term NOT LIKE %s",(linkID,hoofdTerm))
    term = ""
    for (result,) in cursor:
        term = result
    return term

def getScorePMID(term,cursor):
    cursor.execute("SELECT pmid, score FROM nodeXarticle WHERE mainterm LIKE %s",(term,))
    totalScore = 0
    pmidDict = {}
    for (pmid, score) in cursor:
        totalScore += int(score)
        pmidDict[pmid] = score
    return pmidDict, totalScore

def getSynonyms(term,cursor):
    cursor.execute("SELECT word FROM keyword WHERE mainterm LIKE %s",(term,))
    synonyms = []
    for (word,) in cursor:
        synonyms.append(word)
    return synonyms

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

def getLink(term,cursor):
    cursor.execute("SELECT link_id FROM nodeXlink WHERE term LIKE %s",(term,))
    links = {}
    results = cursor.fetchall()
    for result in results:
        link_id = result[0]
        links[link_id] = getLinkScore(link_id,cursor)
    return links

def getLinkScore(link,cursor):
    cursor.execute("SELECT relation_score FROM link WHERE link_id LIKE %s",(link,))
    score = 0
    for (item,) in cursor:
        score = int(item)
    return score

@app.route("/")
def test():
    return getData()

if __name__ == '__main__':
    app.run(debug=True)
