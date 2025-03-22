from UI.HomePage import Ui_MainWindow
from UI.SignUpExt import SignUpExt
from UI.LoginExt import LoginExt
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication

class HomePageExt(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setupSignalAndSlot()

    def setupSignalAndSlot(self):
        self.ui.pushButtonSignUp.clicked.connect(self.xuly_dangky)
        self.ui.pushButtonLogIn.clicked.connect(self.xuly_dangnhap)

    def xuly_dangky(self):
        self.signup_window = SignUpExt()
        self.signup_window.show()
        self.hide()

    def xuly_dangnhap(self):
        self.signin_window = LoginExt()
        self.signin_window.show()
        self.hide()

    def showWindow(self):
        self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePageExt()
    window.show()
    sys.exit(app.exec())