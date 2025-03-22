import traceback
from PyQt6.QtWidgets import QMainWindow, QMessageBox, QApplication
from UI.Login import Ui_MainWindow
from UI.HomePageLoginExt import HomePageLoginExt
from libs.customerconnector import CustomerConnector


class LoginExt(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.custconnector = CustomerConnector()
        self.parent_window = parent
        self.ui.pushButtonLogin.clicked.connect(self.xuly_dangnhap)
    def xuly_dangnhap(self):
        try:
            username = self.ui.lineEditUsername.text()
            password = self.ui.lineEditPassword.text()
            self.custconnector.connect()
            self.nvlogin = self.custconnector.dang_nhap(username, password)

            if self.nvlogin is not None:
                self.homepage_login = HomePageLoginExt(self)
                self.homepage_login.show()
                self.hide()
            else:
                QMessageBox.critical(self, "Login failed",
                                     "You have failed to log in.\nPlease check your login information again.")

        except Exception as e:
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Important: {str(e)}")


