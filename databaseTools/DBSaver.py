#############################################
# Methodes om gegevens van de               #
# textmining op te slaan in                 #
# de databank.                              #
#############################################
# Opmerking: "Vele methodes zullen private  #
# zijn door middel van __ voor de naam.     #
# Hiervoor is gekozen aangezien de meeste   #
# methodes niet bedoeld zijn om van         #
# buiten af te gebruiken."                  #
#############################################
# Gemaakt door: Alex Janse                  #
# Versie 1.0.0.                             #
# Datum: 25-05-2018                         #
#############################################

import DBConnector as dbc                               # wordt gebruikt om de cursor en de connectie object op te halen
import DBLoader as dbl
import traceback                                        # Wordt gebruikt om de volledige error te krijgen ipv alleen de titel

# Hoofd methode die de sub methodes aanroept om de verschillende directories op te slaan
def save(synonymDict, pmidDict, linkDict):
    try:
        cursor, connection = dbc.connect()              # De cursor en connection objecten worden op gehaald om queries te kunnen uitvoeren en de verbinding te verbreken
        __save_PMID(pmidDict, cursor)                    # De __save_PMID wordt aangeroepen om de gegevens van de pmidDict op te slaan in de db
        __save_terms(synonymDict, cursor)
        __save_links(linkDict, cursor)
        __commit(cursor)                                # De __commit methode wordt aangeroepen als er geen exceptions zijn geweest en de queries die zijn uitgevoerd bevestigd kunnen worden in de db
        connection.disconnect()                         # Verbreek de connectie met de db
        dbl.get_data()                                   # maak van de db een JSON
    except Exception as e:
        print(str(traceback.format_exc()))              # Laat de error zien als deze heeft plaats gevonden. Vanwege de brede scala aan SQL errors is er voor gekozen om de algemene Exception te pakken en de details te laten printen voor de developer

# Methode om de gegevens uit de dictonary te halen
# en de methodes aan te roepen die ze vervolgens op slaat
def __save_terms(dict, cursor):
    for mainterm in dict.keys():
        valueList = dict[mainterm]                      # Bevat [[synonymen],[pmid],category]
        category = valueList[2]
        pmid = valueList[1]
        synonymList = valueList[0]
        __save_category(category, cursor)
        __save_main_term(mainterm, category, cursor)
        __save_term_PMID(pmid, mainterm, cursor)
        for synonym in synonymList:
            __save_synonym(synonym, mainterm, cursor)

# Methode om de category op te slaan als deze nog niet in de db staat
def __save_category(category, cursor):
    if __check_uniqueness("type", "classification", category, cursor):            # sla alleen op als het uniek is
        cursor.execute("INSERT INTO type VALUES (%s)", (category,))

# Methode om de hoofdterm op te slaan
def __save_main_term(term, category, cursor):
    if __check_uniqueness("node", "mainterm", term, cursor):
        cursor.execute("INSERT INTO node VALUES (%s,%s)",(term,category))

# Methode om de connectie tussen de hoofdterm en de artikelen op te slaan
def __save_term_PMID(pmidDict, term, cursor):
    for pmid in pmidDict.keys():
        score = pmidDict[pmid]
        if __check_uniqueness("nodeXarticle", "mainterm", term, cursor, " AND pmid LIKE \"" + pmid + "\""):
            cursor.execute("INSERT INTO nodeXarticle VALUES (%s,%s,%s)",(term,pmid,score))

# Methode om te controleren of de data al in de db staat
def __check_uniqueness(tableName, columnName,
                       searchTerm, cursor, extraSQL = ""):
    query = "SELECT "+columnName+" FROM "+tableName+" WHERE "+columnName+" LIKE %s"
    if extraSQL != "":
        query += extraSQL
    cursor.execute(query,(searchTerm,))
    count = 0
    for (resultaat,) in cursor:
        count += 1
    if count > 0:
        return False
    else:
        return True

# Methode om synonymen van de hoofdterm op te slaan
def __save_synonym(synonym, mainterm, cursor):
    if __check_uniqueness("keyword", "word", synonym, cursor, " AND mainterm LIKE \"" + mainterm + "\""):
        cursor.execute("INSERT INTO keyword VALUES (default,%s,%s)",(synonym,mainterm))

# Methode om de requests te verzilveren in de db
def __commit(cursor):
    cursor.execute("COMMIT")

# Methode om de artikelen op te slaan in de db
def __save_PMID(dict, cursor):
    for id in dict.keys():
        if __check_uniqueness("pubmed_article", "pmid", id, cursor):
            data = dict[id]
            cursor.execute("INSERT INTO pubmed_article VALUES (%s,%s,%s,%s)",
                           (id,data[0],data[1],data[2]))

# Methode om de links tussen de nodes op te slaan
def __save_links(dict, cursor):
    for term in dict.keys():
        linkTermDict = dict[term]
        for linkterm in linkTermDict.keys():
            pmidList = linkTermDict[linkterm]
            linkID = __get_link_ID(cursor)
            score = __get_total_score(term, linkterm, pmidList, cursor)
            cursor.execute("INSERT INTO link VALUES (%s,%s)",(linkID,score))
            __insert_node_link(term, linkID, cursor)
            __insert_node_link(linkterm, linkID, cursor)

# Methode om een nieuwe link_id te krijgen
def __get_link_ID(cursor):
    cursor.execute("SELECT link_id FROM link")
    row = cursor.fetchone()
    maxID = 0
    while row is not None:
        if int(row[0]) > maxID:
            maxID = int(row[0])
        row = cursor.fetchone()
    maxID += 1
    return maxID

# Methode om de link tussen nodes op te slaan
def __insert_node_link(term, linkID, cursor):
    cursor.execute("INSERT INTO nodeXlink VALUES (%s,%s)", (linkID, term))

# Methode om de score tussen twee nodes te bepalen
def __get_total_score(term, linkterm, pmidList, cursor):
    totalScore = 0
    for pmid in pmidList:
        totalScore += (__get_score(term, pmid, cursor) + __get_score(linkterm, pmid, cursor))
    return totalScore

# Methode om de score van een artikel op een node te bepalen
def __get_score(term, pmid, cursor):
    cursor.execute("SELECT score FROM nodeXarticle WHERE mainterm LIKE %s AND pmid LIKE %s",(term,pmid))
    score = 0
    for foundScore in cursor:
        score = int(foundScore[0])
    return score

