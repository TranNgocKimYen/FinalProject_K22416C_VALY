import sys
import os
import random
import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QApplication, QMessageBox
from PyQt6.QtGui import QFont, QPixmap
from UI.HomePageLogin import Ui_MainWindow
from UI.ContentBasedResultExt import ContentBasedResultExt, content_based
from UI.HomePageAfterRatingExt import HomePageAfterRatingExt
from dataset.models.restaurant_rater import restaurant_rater
from dataset.models.cf_recommender import cf_model
from libs.reviewconnector import load_data
from libs.photosconnector import load_photos_from_mysql
from UI.SearchResultExt import SearchResultExt
import numpy as np
from surprise import SVD, Dataset, Reader
from surprise.model_selection import cross_validate

# Paths
reviews_path = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\reviews.pkl"
updated_reviews_path = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\updated_reviews.csv"
recommendations_path = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\recommendations.csv"
photos_folder = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\photos"

# Load reviews data
try:
    reviews = load_data()
    if reviews is None or not isinstance(reviews, pd.DataFrame) or reviews.empty:
        raise ValueError("Failed to load reviews data or data is empty")
    print("Loaded reviews data successfully!")
except Exception as e:
    print(f"Error: {e}")
    exit()

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

def rate_and_recommend(df, num=10):
    """A function to randomly select *num* restaurants for users to review."""
    restaurants = restaurant_rater(df, num=num)
    # Load photos_df từ MySQL
    photos_df = load_photos_from_mysql()
    if photos_df is not None and 'business_id' in restaurants.columns:
        restaurants = restaurants.merge(photos_df[['photo_id', 'business_id']], on='business_id', how='left')
    else:
        restaurants['photo_id'] = None
    return restaurants

def save_ratings(updated_df):
    """Save the review data to a CSV file."""
    try:
        updated_df.to_csv(updated_reviews_path, index=False)
        print(f"Saved ratings to {updated_reviews_path}")
        return True
    except Exception as e:
        print(f"Error saving ratings: {e}")
        return False

def generate_recommendations(df, num=10, location=None, name=None, text=None, model_path=r'C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\models\svdmodel.zip'):
    """Generate recommendations based on user reviews."""
    recommendations = cf_model(df=df, num=num, location=location, name=name, text=text, model_path=model_path)
    try:
        recommendations.to_csv(recommendations_path, index=False)
        print(f"Saved recommendations to {recommendations_path}")
    except Exception as e:
        print(f"Error saving recommendations: {e}")
    return recommendations

class HomePageLoginExt(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.content_window = None
        self.rating_page = None
        self.reviews = load_data()
        if 'user_rating' not in self.reviews.columns:
            self.reviews['user_rating'] = None
        self.initialize_ui()
        self.setup_signals()

    def showWindow(self):
        self.show()

    def setup_signals(self):
        self.pushButtonSkip.clicked.connect(self.go_to_content)
        self.pushButtonSubmit.clicked.connect(self.submit_ratings)
        self.pushButtonRecommend.clicked.connect(self.show_recommendations)
        self.pushButtonSearch.clicked.connect(self.search_restaurant)

    def initialize_ui(self):
        self.displayed_restaurants = rate_and_recommend(self.reviews, num=10)
        self.display_restaurants(self.displayed_restaurants)

    def display_restaurants(self, restaurants):
        """Display the list of restaurants on the interface, including images."""
        if restaurants.empty:
            QMessageBox.warning(self, "Error", "There is no restaurant data!")
            return

        try:
            label_names = [getattr(self, f"labelName{i}") for i in range(1, 11)]
            label_locations = [getattr(self, f"labelLocation{i}") for i in range(1, 11)]
            label_categories = [getattr(self, f"labelCategories{i}") for i in range(1, 11)]
            label_ratings = [getattr(self, f"labelRate{i}") for i in range(1, 11)]
            figure_labels = [getattr(self, f"labelFigure{i}") for i in range(1, 11)]
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"Can not find widget: {e}")
            return

        # Format the font.
        name_font = QFont("Georgia", 16, QFont.Weight.Bold)
        other_font = QFont("Georgia", 14)

        # Prepare the data list.
        names = restaurants['name'].tolist()
        locations = restaurants['location'].tolist()
        categories = restaurants['categories'].tolist()
        ratings = restaurants['bs_rating'].tolist()
        photo_ids = restaurants['photo_id'].tolist() if 'photo_id' in restaurants.columns else [None] * len(restaurants)

        # Debug: Print the data for checking.
        print("Debug - Data to display:")
        for i in range(min(10, len(names))):
            print(f"Index {i}: {names[i]}, {ratings[i]}, {locations[i]}, {categories[i]}, {photo_ids[i]}")

        # Assign data and images to the interface.
        for i in range(10):
            if i < len(names):
                # Remove double quotes from the beginning and end of the string.
                name = str(names[i]).strip('"') if names[i] and str(names[i]).strip() else "N/A"
                location = str(locations[i]).strip('"') if locations[i] and str(locations[i]).strip() else "N/A"
                category = str(categories[i]).strip('"') if categories[i] and str(categories[i]).strip() else "N/A"
                rating = str(ratings[i]).strip('"') if pd.notna(ratings[i]) else "Not rated"

                label_names[i].setText(name)
                label_names[i].setFont(name_font)
                label_locations[i].setText(location)
                label_locations[i].setFont(other_font)
                label_categories[i].setText(category)
                label_categories[i].setFont(other_font)
                label_ratings[i].setText(rating)
                label_ratings[i].setFont(other_font)

                # Assign images
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
                label_locations[i].setText("")
                label_categories[i].setText("")
                label_ratings[i].setText("")
                figure_labels[i].setText("")

    def go_to_content(self):
        """Switch to the ContentBasedResultExt interface when Skip is pressed."""
        print("Skipping to content window")
        self.content_window = ContentBasedResultExt(homepage_instance=self)
        self.content_window.showWindow()
        self.hide()

    def submit_ratings(self):
        """Process and save user reviews."""
        if not hasattr(self, "displayed_restaurants") or self.displayed_restaurants.empty:
            QMessageBox.warning(self, "Error", "There are no restaurants to review!")
            return

        errors = []
        has_valid_rating = False

        try:
            rating_inputs = [getattr(self, f"lineEditRating{i}") for i in range(1, 11)]
        except AttributeError as e:
            QMessageBox.critical(self, "Error", f"Input field not found: {e}")
            return

        for i, (index, restaurant) in enumerate(self.displayed_restaurants.iterrows()):
            rating_text = rating_inputs[i].text().strip()
            if rating_text:
                try:
                    rating = float(rating_text)
                    if 1 <= rating <= 5:
                        self.displayed_restaurants.at[index, "user_rating"] = rating
                        if 'business_id' in self.reviews.columns and 'business_id' in restaurant:
                            self.reviews.loc[
                                self.reviews['business_id'] == restaurant['business_id'], 'user_rating'] = rating
                        elif 'name' in self.reviews.columns:
                            self.reviews.loc[self.reviews['name'] == restaurant['name'], 'user_rating'] = rating
                        has_valid_rating = True
                    else:
                        errors.append(f"Invalid rating for {restaurant['name']} (must be 1-5).")
                except ValueError:
                    errors.append(f"Please enter a valid number for {restaurant['name']}.")
            else:
                self.displayed_restaurants.at[index, "user_rating"] = None

        if errors:
            QMessageBox.warning(self, "Error", "\n".join(errors))
            return

        if not has_valid_rating:
            QMessageBox.warning(self, "Error", "You haven't entered any reviews!")
            return

        if save_ratings(self.reviews):
            QMessageBox.information(self, "Success", "The review has been saved!")
        else:
            QMessageBox.warning(self, "Error", "Failed to save ratings!")


    def show_recommendations(self):
        """Display the recommendation page after pressing Recommend."""
        if not hasattr(self, "displayed_restaurants") or self.displayed_restaurants.empty:
            QMessageBox.warning(self, "Error", "There is no data to generate suggestions!")
            return

        if 'business_id' in self.reviews.columns and 'business_id' in self.displayed_restaurants.columns:
            for _, row in self.displayed_restaurants.iterrows():
                self.reviews.loc[self.reviews['business_id'] == row['business_id'], 'user_rating'] = row['user_rating']
        elif 'name' in self.reviews.columns:
            for _, row in self.displayed_restaurants.iterrows():
                self.reviews.loc[self.reviews['name'] == row['name'], 'user_rating'] = row['user_rating']

        if not save_ratings(self.reviews):
            QMessageBox.warning(self, "Error", "Failed to save reviews before generating recommendations!")
            return

        # Load data from the saved file.
        try:
            updated_reviews = pd.read_csv(updated_reviews_path)
            if updated_reviews.empty:
                QMessageBox.warning(self, "Error", "The saved reviews file is empty!")
                return
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load saved reviews: {e}")
            return

        recommendations = generate_recommendations(df=updated_reviews, num=10)

        if recommendations.empty:
            QMessageBox.warning(self, "Error", "Can not create restaurant recommendations!")
            return

        try:
            self.rating_page = HomePageAfterRatingExt(recommendations, parent=self)
            self.hide()
            self.rating_page.show()
        except Exception as e:
            print(f"Error displaying HomePageAfterRatingExt: {e}")
            QMessageBox.critical(self, "Error", f"Unable to display the suggestion page: {e}")
    def search_restaurant(self):
        """Process restaurant search by name and display the result"""
        search_name = self.lineEditSearch.text().strip()

        if not search_name:
            QMessageBox.warning(self, "Error", "Please enter a restaurant name to search!")
            return

        if self.reviews is None or self.reviews.empty:
            QMessageBox.critical(self, "Error", "Review data is not available!")
            return

        try:
            recommendations = content_based(df=self.reviews, name=search_name, num=10)

            if recommendations is None or recommendations.empty:
                QMessageBox.warning(self, "No Results", f"No similar restaurants found for '{search_name}'!")
                return

            # Display the results on the SearchResultExt
            self.result_window = SearchResultExt(recommendations, parent=self)
            self.result_window.showWindow()
            self.hide()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to search: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HomePageLoginExt()
    window.showWindow()
    sys.exit(app.exec())