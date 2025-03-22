import sys
from PyQt6.QtWidgets import QMainWindow, QApplication
from UI.HomePageExt import HomePageExt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePageExt()
    window.show()  # Gọi show() từ QMainWindow
    sys.exit(app.exec())



