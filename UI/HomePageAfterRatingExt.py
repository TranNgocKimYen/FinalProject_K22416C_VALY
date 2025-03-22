import sys
import os
import random
import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from UI.HomePageAfterRating import Ui_HomePageAfterRating
from UI.RatingDialogExt import RatingDialogExt
from libs.photosconnector import load_photos_from_mysql

# Paths
recommendations_path = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\recommendations.csv"
photos_folder = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\photos"

def get_random_image(photos_folder):
    try:
        image_files = [f for f in os.listdir(photos_folder) if f.endswith('.jpg')]
        if not image_files:
            return None
        random_image = random.choice(image_files)
        return os.path.join(photos_folder, random_image)
    except Exception as e:
        print(f"Error selecting random image: {e}")
        return None

def load_recommendations_with_photos(recommendations):
    """Load recommendations và merge with photo"""
    try:
        if recommendations is None or recommendations.empty:
            raise ValueError("Recommendations data is empty or None")
        print("Recommendations data provided successfully!")

        # Load photos_df from MySQL
        photos_df = load_photos_from_mysql()
        if photos_df is not None and 'business_id' in recommendations.columns:
            recommendations = recommendations.merge(photos_df[['photo_id', 'business_id']], on='business_id', how='left')
        else:
            recommendations['photo_id'] = None

        return recommendations
    except Exception as e:
        print(f"Error processing recommendations: {e}")
        return recommendations

class HomePageAfterRatingExt(QMainWindow, Ui_HomePageAfterRating):
    def __init__(self, recommendations, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.parent = parent
        self.recommendations = load_recommendations_with_photos(recommendations)
        self.rating_buttons = []
        self.initialize_ui()
        self.setup_signals()

    def showWindow(self):
        self.show()

    def setup_signals(self):
        try:
            self.pushButtonWritePrevious.clicked.connect(self.go_back)
            self.pushButtonLogOut.clicked.connect(self.log_out)
            for i in range(10):
                if i < len(self.rating_buttons) and self.rating_buttons[i]:
                    self.rating_buttons[i].clicked.connect(lambda checked, idx=i: self.open_rating_dialog(idx))
                    print(f"Connected pushButtonRating{i + 1} to open_rating_dialog")
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"Can not find Back button or Rating button: {e}")

    def initialize_ui(self):
        self.display_recommendations()

    def log_out(self):
        from UI.HomePageExt import HomePageExt

        """Handle logout action by redirecting to the main HomePageExt."""
        print("Logging out...")
        self.close()
        self.home_page = HomePageExt()
        self.home_page.showWindow()

    def display_recommendations(self):
        """Display the recommendation list on the interface, including images."""
        print("Entering display_recommendations")
        if self.recommendations.empty or len(self.recommendations) < 1:
            QMessageBox.warning(self, "Error", "No recommendations to display!")
            return

        try:
            label_names = [getattr(self, f"labelName{i}") for i in range(1, 11)]
            label_categories = [getattr(self, f"labelCategories{i}") for i in range(1, 11)]
            label_locations = [getattr(self, f"labelLocation{i}") for i in range(1, 11)]
            label_rates = [getattr(self, f"labelRate{i}") for i in range(1, 11)]
            figure_labels = [getattr(self, f"labelFigure{i}") for i in range(1, 11)]
            self.rating_buttons = [getattr(self, f"pushButtonRating{i}") for i in range(1, 11)]
            print("Widgets retrieved successfully")
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"Can not find widget: {e}")
            return


        name_font = QFont("Georgia", 16, QFont.Weight.Bold)
        other_font = QFont("Georgia", 14)


        names = self.recommendations['name'].tolist()
        categories = self.recommendations['categories'].tolist() if 'categories' in self.recommendations.columns else [None] * len(self.recommendations)
        locations = self.recommendations['location'].tolist()
        ratings = self.recommendations['bs_rating'].tolist()
        photo_ids = self.recommendations['photo_id'].tolist() if 'photo_id' in self.recommendations.columns else [None] * len(self.recommendations)


        print("Debug - Data to display:")
        for i in range(min(10, len(names))):
            print(f"Index {i}: {names[i]}, {categories[i]}, {ratings[i]}, {locations[i]}, {photo_ids[i]}")


        for i in range(10):
            if i < len(self.recommendations):
                rec = self.recommendations.iloc[i]
                name = str(rec["name"]).strip('"') if pd.notna(rec["name"]) and str(rec["name"]).strip() else "N/A"
                location = str(rec["location"]).strip('"') if pd.notna(rec["location"]) and str(rec["location"]).strip() else "N/A"
                rating = str(rec["bs_rating"]).strip('"') if pd.notna(rec["bs_rating"]) else "Not rated"
                category = str(rec["categories"]).strip('"') if 'categories' in rec and pd.notna(rec["categories"]) and str(rec["categories"]).strip() else "N/A"
                label_names[i].setText(name)
                label_names[i].setFont(name_font)
                label_categories[i].setText(category)
                label_categories[i].setFont(other_font)
                label_locations[i].setText(location)
                label_locations[i].setFont(other_font)
                label_rates[i].setText(rating)
                label_rates[i].setFont(other_font)
                self.rating_buttons[i].setEnabled(True)

                # Set images
                figure_labels[i].setScaledContents(True)
                if pd.notna(photo_ids[i]):
                    photo_path = os.path.join(photos_folder, f"{photo_ids[i]}.jpg")
                    if os.path.exists(photo_path):
                        pixmap = QPixmap(photo_path)
                        figure_labels[i].setPixmap(pixmap)
                    else:
                        random_path = get_random_image(photos_folder)
                        if random_path and os.path.exists(random_path):
                            pixmap = QPixmap(random_path)
                            figure_labels[i].setPixmap(pixmap)
                        else:
                            figure_labels[i].setText("No image available")
                else:
                    random_path = get_random_image(photos_folder)
                    if random_path and os.path.exists(random_path):
                        pixmap = QPixmap(random_path)
                        figure_labels[i].setPixmap(pixmap)
                    else:
                        figure_labels[i].setText("No image available")
            else:
                label_names[i].setText("")
                label_categories[i].setText("")
                label_locations[i].setText("")
                label_rates[i].setText("")
                figure_labels[i].setText("")
                if i < len(self.rating_buttons):
                    self.rating_buttons[i].setEnabled(False)

    def go_back(self):
        """Come back previous page."""
        self.close()
        if self.parent:
            self.parent.showWindow()

    def open_rating_dialog(self, index):
        """Open dialog to rate"""
        if index >= len(self.recommendations):
            return

        rec = self.recommendations.iloc[index]
        restaurant_info = {
            "name": str(rec["name"]).strip('"'),
            "location": str(rec["location"]).strip('"'),
            "categories": str(rec["categories"]).strip('"') if 'categories' in rec else "N/A",
            "bs_rating": str(rec["bs_rating"]).strip('"')
        }

        try:
            dialog = RatingDialogExt(restaurant_info, parent=self)
            print("RatingDialogExt created successfully")
            if dialog.exec():
                rating, review = dialog.get_rating_and_review()
                print(f"Rating for {restaurant_info['name']}: {rating}, Review: {review}")
                if 'user_rating' not in self.recommendations.columns:
                    self.recommendations['user_rating'] = None
                if 'review' not in self.recommendations.columns:
                    self.recommendations['review'] = None
                self.recommendations.at[self.recommendations.index[index], 'user_rating'] = rating
                self.recommendations.at[self.recommendations.index[index], 'review'] = review

                try:
                    self.recommendations.to_csv(recommendations_path, index=False)
                    print(f"Saved updated recommendations to {recommendations_path}")
                    QMessageBox.information(self, "Success", "Your rating has been saved!")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Can not save file CSV: {e}")
            else:
                print("Rating dialog cancelled")
        except Exception as e:
            print(f"Error opening RatingDialogExt: {e}")
            QMessageBox.critical(self, "Error", f"Can not open RatingDialogExt: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dummy_data = pd.DataFrame({
        'business_id': ['b1', 'b2', 'b3'],
        'name': ['"Restaurant 1"', '"Restaurant 2"', '"Restaurant 3"'],
        'location': ['"Location 1"', '"Location 2"', '"Location 3"'],
        'categories': ['"Italian"', '"Chinese"', '"Mexican"'],
        'bs_rating': ['"4.5"', '"4.0"', '"3.8"'],
        'photo_id': ['photo1', 'photo2', 'photo3']
    })
    window = HomePageAfterRatingExt(dummy_data)
    window.showWindow()
    sys.exit(app.exec())