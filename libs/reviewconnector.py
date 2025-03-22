from libs.connectors import MySQlConnector
import pymysql
import pandas as pd

def load_data():
    connector = MySQlConnector()
    conn = connector.connect()
    if conn is None:
        print("There is no connection to the database!")
        return None
    try:
        cursor = conn.cursor()
        query = "SELECT * FROM reviews;"
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        dataset = cursor.fetchall()
        data = pd.DataFrame(dataset, columns=columns)
        cursor.close()
        conn.close()
        return data

    except pymysql.Error as e:
        print(f"Error when querying data: {e}")
        return None

