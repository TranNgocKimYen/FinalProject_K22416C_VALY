import pickle
import os
import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QLabel, QPushButton, QApplication, QMessageBox
from PyQt6.QtGui import QFont, QPixmap
from UI.ContentBasedResult import Ui_MainWindow
from dataset.models.features import stem_and_tokenize, stopwords
from sklearn.metrics.pairwise import cosine_similarity
from UI.RatingDialogExt import RatingDialogExt
from libs.photosconnector import load_photos_from_mysql

# Paths
cosine_similarity_path = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\cosine_similarity.pkl"
data_path = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\data.pkl"
photos_folder = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\photos"
recommendations_path = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\recommendations.csv"

# Load cosine_similarity and df
try:
    with open(cosine_similarity_path, 'rb') as file:
        cosine_similarity = pickle.load(file)
    print("Loaded cosine_similarity.pkl successfully!")
    with open(data_path, 'rb') as file:
        df = pickle.load(file)
    print("Loaded data.pkl successfully!")
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()
except Exception as e:
    print(f"Unexpected error: {e}")
    exit()

def content_based(df, name: str = None, rating: int = 1, num: int = 10, text: str = None, location: str = None):
    import random
    df_original = df.copy()
    df = df.drop_duplicates(subset=['name'], keep='first')

    if name:
        matched_restaurants = df[df['name'].str.contains(name, case=False, na=False)]

        if matched_restaurants.empty:
            print(f"No restaurants found containing: {name}")
            return pd.DataFrame()

        index_ = matched_restaurants.index[0]

        sim = list(enumerate(cosine_similarity[index_]))
        sim = sorted(sim, key=lambda x: x[1], reverse=True)[1:]
        # Remove duplicates in indices while preserving order and ensuring the required number (`num`).
        indices = []
        seen = set()
        for i in [i[0] for i in sim]:
            name_at_index = df_original.iloc[i]['name']
            if name_at_index not in seen:
                seen.add(name_at_index)
                indices.append(i)
            if len(indices) >= num:
                break
        indices = indices[:num]
        print(f"Top {len(indices)} Restaurants Like [{name}]")

        if location:
            df = df.loc[(df['bs_rating'] >= rating) & (df.location.str.contains(location, case=False, na=False))]
        else:
            df = df.loc[(df['bs_rating'] >= rating)]

        indices = [i for i in indices if i in df.index]
        df = df.loc[
            indices, ('business_id', 'name', 'bs_rating', 'review_count', 'location', 'categories')
        ].sort_values('bs_rating', ascending=False)

        result_df = df.reset_index(drop=True)
    else:
        if text:
            text = text.lower()
            tokens = stem_and_tokenize(text)
            tokens = [word for word in tokens if word not in stopwords]
            text_set = set(tokens)
            if location:
                df = df.loc[(df.location.str.contains(location)) & (df['bs_rating'] >= rating)].reset_index(drop=True)
            vectors = []
            for words in df.details:
                words = words.lower()
                words = stem_and_tokenize(words)
                words = [word for word in words if word not in stopwords]
                words = set(words)
                vector = text_set.intersection(words)
                vectors.append(len(vector))
            vectors = sorted(list(enumerate(vectors)), key=lambda x: x[1], reverse=True)

            indices = []
            seen = set()
            for i in [i[0] for i in vectors]:
                name_at_index = df.iloc[i]['name']
                if name_at_index not in seen:
                    seen.add(name_at_index)
                    indices.append(i)
                if len(indices) >= num:
                    break
            indices = indices[:num]
            print(f"Top {len(indices)} Best Restaurants Based on Entered Text: '{text}'")
            df = df.loc[
                indices, ('business_id', 'name', 'bs_rating', 'review_count', 'location', 'categories')].sort_values(
                by=['bs_rating', 'review_count'], ascending=False)
            result_df = df.reset_index(drop=True)
        elif location:
            df = df.loc[df.location.str.contains(location) & (df['bs_rating'] >= rating)]
            df = df.sort_values(['review_count', 'bs_rating'], ascending=False)[:num]
            print(f"Top {num} Restaurants in {location}")
            result_df = df[['business_id', 'name', 'bs_rating', 'review_count', 'location', 'categories']].reset_index(
                drop=True)
        else:
            df = df.loc[df['bs_rating'] >= rating].sort_values(by=['review_count', 'bs_rating'], ascending=False)[:num]
            print(f"Top {num} Most Popular Restaurants")
            result_df = df[['business_id', 'name', 'bs_rating', 'review_count', 'location', 'categories']].reset_index(
                drop=True)
            print(result_df)

    if result_df.empty:
        print("No recommendations found!")
        return result_df

    # Retrieve images from the database.
    import random

    photos_df = load_photos_from_mysql()
    if photos_df is not None and not photos_df.empty:
        result_df = result_df.merge(photos_df[['photo_id', 'business_id']], on='business_id', how='left')
        available_photos = photos_df['photo_id'].dropna().tolist()
        result_df['photo_id'] = result_df['photo_id'].apply(
            lambda x: x if pd.notna(x) else random.choice(available_photos))
    else:
        default_photos = ["default1.jpg", "default2.jpg", "default3.jpg"]
        result_df['photo_id'] = [random.choice(default_photos) for _ in range(len(result_df))]
    return result_df[['name', 'bs_rating', 'review_count', 'location', 'categories', 'photo_id']]

class ContentBasedResultExt(QMainWindow, Ui_MainWindow):
    def __init__(self, homepage_instance=None):
        super().__init__()
        self.setupUi(self)
        self.homepage_instance = homepage_instance
        self.pushButtonWritePrevious.clicked.connect(self.go_to_homepage)
        self.initialize_results()
        self.setup_rating_buttons()

    def showWindow(self):
        self.show()

    def go_to_homepage(self):
        if self.homepage_instance:
            print("Opening HomePageLoginExt")
            self.close()
            self.homepage_instance.showWindow()
        else:
            print("No homepage instance provided")

    def initialize_results(self):
        name = self.lineEdit_name.text().strip() if hasattr(self, 'lineEdit_name') else None
        text = self.lineEdit_text.text().strip() if hasattr(self, 'lineEdit_text') else None
        location = self.lineEdit_location.text().strip() if hasattr(self, 'lineEdit_location') else None
        rating = int(self.spinBox_rating.value()) if hasattr(self, 'spinBox_rating') else 1
        num = int(self.spinBox_num.value()) if hasattr(self, 'spinBox_num') else 10

        result_df = content_based(df=df, name=name or None, rating=rating, num=num, text=text or None, location=location or None)
        self.display_results(result_df)

    def display_results(self, result_df):
        name_buttons = [
            self.labelName1, self.labelName2, self.labelName3, self.labelName4, self.labelName5,
            self.labelName6, self.labelName7, self.labelName8, self.labelName9, self.labelName10
        ]
        category_labels = [
            self.labelCategories1, self.labelCategories2, self.labelCategories3, self.labelCategories4,
            self.labelCategories5,
            self.labelCategories6, self.labelCategories7, self.labelCategories8, self.labelCategories9,
            self.labelCategories10
        ]
        rating_labels = [
            self.labelRate1, self.labelRate2, self.labelRate3, self.labelRate4, self.labelRate5,
            self.labelRate6, self.labelRate7, self.labelRate8, self.labelRate9, self.labelRate10
        ]
        location_labels = [
            self.labelLocation1, self.labelLocation2, self.labelLocation3, self.labelLocation4,
            self.labelLocation5,
            self.labelLocation6, self.labelLocation7, self.labelLocation8, self.labelLocation9,
            self.labelLocation10
        ]
        figure_labels = [
            self.labelFigure1, self.labelFigure2, self.labelFigure3, self.labelFigure4, self.labelFigure5,
            self.labelFigure6, self.labelFigure7, self.labelFigure8, self.labelFigure9, self.labelFigure10
        ]
        for label in figure_labels:
            label.setScaledContents(True)

        name_font = QFont()
        name_font.setPointSize(20)
        name_font.setBold(True)

        other_font = QFont()
        other_font.setPointSize(12)
        other_font.setBold(True)

        # Get data result_df
        names = result_df['name'].tolist()
        categories = result_df['categories'].tolist()
        ratings = result_df['bs_rating'].tolist()
        locations = result_df['location'].tolist()
        photo_ids = result_df['photo_id'].tolist()

        print("Debug - Data to display:")
        for i in range(min(10, len(names))):
            print(f"Index {i}: {names[i]}, {ratings[i]}, {locations[i]}, {categories[i]}, {photo_ids[i]}")

        # Assign data vào các label
        for i in range(10):
            if i < len(names):
                name_buttons[i].setText(str(names[i]).strip('"'))
                name_buttons[i].setFont(name_font)
                category_labels[i].setText(str(categories[i]).strip('"'))
                category_labels[i].setFont(other_font)
                category_labels[i].setWordWrap(True)
                rating_labels[i].setText(str(ratings[i]))
                rating_labels[i].setFont(other_font)
                rating_labels[i].setWordWrap(True)
                location_labels[i].setText(str(locations[i]).strip('"'))
                location_labels[i].setFont(other_font)
                location_labels[i].setWordWrap(True)
                if pd.notna(photo_ids[i]):
                    photo_path = os.path.join(photos_folder, f"{photo_ids[i]}.jpg")
                    if os.path.exists(photo_path):
                        pixmap = QPixmap(photo_path)
                        figure_labels[i].setPixmap(pixmap)
                    else:
                        figure_labels[i].setText("Image not found")
                else:
                    figure_labels[i].setText("No image")
            else:
                name_buttons[i].setText("")
                category_labels[i].setText("")
                rating_labels[i].setText("")
                location_labels[i].setText("")
                figure_labels[i].setText("")

    def setup_rating_buttons(self):
        """Connect rating button with popup RatingDialog"""
        self.rating_buttons = [
            self.pushButtonRating1, self.pushButtonRating2, self.pushButtonRating3, self.pushButtonRating4,
            self.pushButtonRating5, self.pushButtonRating6, self.pushButtonRating7, self.pushButtonRating8,
            self.pushButtonRating9, self.pushButtonRating10
        ]
        for i, button in enumerate(self.rating_buttons):
            if button:
                button.clicked.connect(lambda checked, idx=i: self.open_rating_dialog(idx))

    def open_rating_dialog(self, index):
        """Open dialog to rate restaurant """
        if index >= len(self.displayed_results):
            return

        rec = self.displayed_results.iloc[index]
        restaurant_info = {
            "name": str(rec["name"]),
            "location": str(rec["location"]),
            "bs_rating": str(rec["bs_rating"])
        }

        try:
            dialog = RatingDialogExt(restaurant_info, parent=self)
            print("RatingDialogExt created successfully")
            if dialog.exec():  # Send
                rating, review = dialog.get_rating_and_review()
                print(f"Rating for {restaurant_info['name']}: {rating}, Review: {review}")
                if 'user_rating' not in self.displayed_results.columns:
                    self.displayed_results['user_rating'] = None
                if 'review' not in self.displayed_results.columns:
                    self.displayed_results['review'] = None
                self.displayed_results.at[self.displayed_results.index[index], 'user_rating'] = rating
                self.displayed_results.at[self.displayed_results.index[index], 'review'] = review

                try:
                    self.displayed_results.to_csv(recommendations_path, index=False)
                    print(f"Saved updated recommendations to {recommendations_path}")
                    QMessageBox.information(self, "Success", "Your rating has been saved!")
                except Exception as e:
                    QMessageBox.warning(self, "Error", f"Can not save file CSV: {e}")
            else:  # Cancel
                print("Rating dialog cancelled")
        except Exception as e:
            print(f"Error opening RatingDialogExt: {e}")
            QMessageBox.critical(self, "Error", f"Can not open RatingDialogExt: {e}")

    def initialize_results(self):
        name = self.lineEdit_name.text().strip() if hasattr(self, 'lineEdit_name') else None
        text = self.lineEdit_text.text().strip() if hasattr(self, 'lineEdit_text') else None
        location = self.lineEdit_location.text().strip() if hasattr(self, 'lineEdit_location') else None
        rating = int(self.spinBox_rating.value()) if hasattr(self, 'spinBox_rating') else 1
        num = int(self.spinBox_num.value()) if hasattr(self, 'spinBox_num') else 10

        self.displayed_results = content_based(df=df, name=name or None, rating=rating, num=num, text=text or None, location=location or None)
        self.display_results(self.displayed_results)

if __name__ == "__main__":
    import sys
    from UI.HomePageLoginExt import HomePageLoginExt
    app = QApplication(sys.argv)
    main_window = QMainWindow()
    homepage = HomePageLoginExt(main_window)
    window = ContentBasedResultExt(homepage_instance=homepage)
    homepage.showWindow()
    sys.exit(app.exec())