class Customer:
    def __init__(self, user_id=None, lastname=None, firstname=None,
                 email=None, zipcode=None, username=None, password=None):
        self.user_id = user_id
        self.lastname = lastname
        self.firstname = firstname
        self.email = email
        self.zipcode = zipcode
        self.username = username
        self.password = password

    def __str__(self):
        return f"Customer({self.user_id}, {self.lastname}, {self.firstname}, {self.email}, {self.zipcode}, {self.username})"
