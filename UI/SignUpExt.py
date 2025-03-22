import traceback
from PyQt6.QtWidgets import QMessageBox, QMainWindow
from UI.SignUp import Ui_MainWindow
from UI.LoginExt import LoginExt
from libs.connectors import MySQlConnector

class SignUpExt(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.db_connector = MySQlConnector()
        self.conn = self.db_connector.connect()
        self.setupUi(self)
        self.pushButtonSignUp1.clicked.connect(self.processInsert)
        self.labelHaveAccount.mousePressEvent = self.haveanaccount

    def showWindow(self):
        self.show()

    def processInsert(self):
        try:
            if not self.conn or not self.conn.open:
                QMessageBox.critical(self, "Error", "No database connection available!")
                return
            cursor = self.conn.cursor()
            sql = """
                INSERT INTO users (lastname, firstname, email, zipcode, username, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            lastname = self.lineEditLastName.text()
            firstname = self.lineEditFirstName.text()
            email = self.lineEditEmail.text()
            zipcode = self.lineEditZipCode.text()
            username = self.lineEditUsername.text()
            password = self.lineEditPassword.text()

            if not self.checkBoxRobot.isChecked():
                QMessageBox.warning(self, "Warning", "Please confirm you are not a robot!")
                return

            val = (lastname, firstname, email, zipcode, username, password)
            cursor.execute(sql, val)
            self.conn.commit()

            print(cursor.rowcount, "record inserted, ID:", cursor.lastrowid)
            cursor.close()
            QMessageBox.information(self, "Success", "Registered successfully !")
            self.openLoginWindow()
        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error occurred: {str(e)}")

    def haveanaccount(self, event):
        self.openLoginWindow()

    def openLoginWindow(self):
        self.close()
        self.login_window = LoginExt()
        self.login_window.show()