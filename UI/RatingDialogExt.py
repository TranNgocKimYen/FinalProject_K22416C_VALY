from PyQt6.QtWidgets import QDialog, QMessageBox
from UI.RatingDialog import Ui_Dialog
import pymysql
from libs.connectors import MySQlConnector

class RatingDialogExt(QDialog):
    def __init__(self, restaurant_info, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.restaurant_info = restaurant_info
        self.db = MySQlConnector()
        self.rating = 0
        self.review = ""
        self.star_buttons = []
        self.setup_stars()
        self.setup_signals()

    def setup_stars(self):
        """Initialize 5 stars for rating"""
        self.star_buttons = [getattr(self.ui, f"pushButton_{i}") for i in range(1, 6)]

        for i, button in enumerate(self.star_buttons):
            button.setText("★")
            button.setStyleSheet("color: black; font-size: 40px; border: none; padding: 0px; margin: 5px;")
            button.setProperty("index", i + 1)

        # Display restaurant information
        self.ui.label_2.setText(f"Rate {self.restaurant_info['name']}\nYour opinion matters to us!")

        self.ui.lineEdit.setStyleSheet("""
            border: 2px solid rgb(229, 229, 229);
            border-radius: 10px;
            font: 12pt "Arial";
            color: rgb(62, 62, 62);
            padding: 10px;
        """)

    def set_rating(self, rating):
        """Update the rating and change the color of the stars"""
        self.rating = rating
        print(f"Selected rating: {self.rating}")

        for i, button in enumerate(self.star_buttons):
            if i < self.rating:
                button.setStyleSheet("color: gold; font-size: 40px; border: none; padding: 0px; margin: 5px;")
            else:
                button.setStyleSheet("color: black; font-size: 40px; border: none; padding: 0px; margin: 5px;")

    def setup_signals(self):
        """Connect the Send and Cancel buttons to the rating stars"""
        self.ui.pushButtonLogOut.clicked.connect(self.submit_rating)
        self.ui.pushButtonLogOut_2.clicked.connect(self.reject)
        for i, button in enumerate(self.star_buttons):
            button.clicked.connect(lambda checked, idx=i + 1: self.set_rating(idx))

    def get_rating_and_review(self):
        """Retrieve the rating and review from the interface."""
        self.review = self.ui.lineEdit.text().strip()
        return self.rating, self.review

    def submit_rating(self):
        """Save the data to the database when the Submit button is pressed"""
        rating, review = self.get_rating_and_review()
        if rating == 0:
            QMessageBox.warning(self, "Warning", "Please select a rating before submitting.")
            return

        business_id = self.restaurant_info.get("name")
        self.save_to_database(business_id, rating, review)
        QMessageBox.information(self, "Success", "Rating submitted successfully!")
        self.accept()

    def save_to_database(self, business_name, rating, review):
        """Save the review to the database"""
        conn = self.db.connect()
        if conn is None:
            QMessageBox.critical(self, "Error", "Failed to connect to the database!")
            return

        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO ratings (business_name, user_rating, review, created_at)
                VALUES (%s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE
                    user_rating = VALUES(user_rating),
                    review = VALUES(review),
                    created_at = NOW()
            """
            params = (business_name, rating, review)
            cursor.execute(query, params)
            conn.commit()
            print("Rating saved successfully!")
        except pymysql.Error as e:
            print(f"Error saving to database: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save rating: {e}")
        finally:
            if conn:
                conn.close()
                print("Database connection closed")