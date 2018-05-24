import DBConnector as dbc
import traceback
import json
from flask import Flask

app = Flask(__name__, instance_relative_config=True)

def getData():
    try:
        cursor, connection = dbc.connect()
        data = createJSONData(cursor)
        connection.close()
        return str(data)
    except Exception as e:
        return str(traceback.format_exc())

def createJSONData(cursor):
    cursor.execute("SELECT * FROM node")
    data = {}
    data["nodes"] = []
    data["links"] = []
    for (term, category) in cursor:
        pmidScoreDict, nodeScore = getScorePMID(term,cursor)
        synonyms = getSynonyms(term,cursor)
        pmidDict = getPMIDData(pmidScoreDict,cursor)
        linkDict = getLink(term, cursor)
        data = createNodes(term, category,nodeScore,synonyms,pmidDict, data)
        data = createLinks(linkDict,term,data,cursor)
    return data

def createNodes(term, category, nodeScore, synonyms, pmidDict, data):
    group = getCatInt(category)
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
    return data

def createLinks(linkDict,hoofdterm,data,cursor):
    for term in linkDict.keys():
        data["links"].append({
            'scource' : hoofdterm,
            'target' : term,
            'value' : linkDict[term]
        })
    return data

def getCatInt(category):
    return 1

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
    for (link_id,) in cursor:
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
