from mysql import connector


def connect():
    connection = connector.connect(user="owe8_pg8",
                             password = "blaat1234",
                             host = "localhost",
                             database="owe8_pg8")
    return connection.cursor(buffered=True), connection


