import pandas as pd
import pymysql

from libs.connectors import MySQlConnector
def load_photos_from_mysql():
    """
    Connect to MySQL and load data from the 'photos' table.
    Return a DataFrame containing *business_id* and *photo_id*, removing duplicates based on *business_id*.
    """
    photos_df = None
    try:
        mysql_conn = MySQlConnector()
        conn = mysql_conn.connect()
        if conn is not None:
            query = "SELECT business_id, photo_id FROM photos"
            photos_df = pd.read_sql(query, conn)
            photos_df = photos_df.drop_duplicates(subset=['business_id'], keep='first')
            conn.close()

        else:
            print("Error: MySQL connection is None")
    except pymysql.Error as e:
        print(f"MySQL error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return photos_df