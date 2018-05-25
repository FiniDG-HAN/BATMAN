from mysql import connector

#########################################
# Methode om verbinding te maken        #
# met de MYSQL databank op cytosine.nl  #
#########################################
# Gemaakt door: Alex Janse              #
# Versie: 1.0.0                         #
# Datum: 25-05-2018                     #
#########################################

def connect():
    try:
        connection = connector.connect(user="owe8_pg8",
                                 password = "blaat1234",
                                 host = "localhost",
                                 database="owe8_pg8")       # Maakt verbinding
        return connection.cursor(buffered=True), connection # Retourneerd een cursor om de query mee te kunnen uitvoeren
                                                            # en de connectie om die te verbreken
    except Exception as e:
        return "ERROR", str(e)


