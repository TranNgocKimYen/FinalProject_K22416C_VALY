from libs.connectors import MySQlConnector
from libs.customer import Customer


class CustomerConnector(MySQlConnector):
    def dang_nhap(self, username, password):
        cursor = self.conn.cursor()
        sql = "SELECT * FROM users WHERE username=%s AND password=%s"
        val = (username, password)
        cursor.execute(sql, val)
        dataset = cursor.fetchone()
        customer = None
        if dataset is not None:
            user_id, lastname, firstname, email, zipcode, username, password = dataset
            customer = Customer(user_id, lastname, firstname, email, zipcode, username, password)
        cursor.close()
        return customer





