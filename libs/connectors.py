import pymysql

class MySQlConnector:
    def __init__(self):
        self.server = "localhost"
        self.port = 8000
        self.database = "restaurant_rs"
        self.username = "root"
        self.password = "Phydy@1311"
        self.conn = None

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.server,
                port=self.port,
                database=self.database,
                user=self.username,
                password=self.password
            )
            return self.conn
        except pymysql.Error as e:
            self.conn = None
            return None

