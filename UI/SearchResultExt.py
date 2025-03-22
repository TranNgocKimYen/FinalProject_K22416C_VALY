import os
import pandas as pd
from PyQt6.QtWidgets import QMainWindow, QMessageBox
from PyQt6.QtGui import QFont, QPixmap
from UI.SearchResult import Ui_SearchResult
from libs.photosconnector import load_photos_from_mysql

photos_folder = r"C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\photos"

class SearchResultExt(QMainWindow, Ui_SearchResult):
    def __init__(self, results_df, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.results_df = results_df
        print("Initial results_df:")
        print(self.results_df)
        self.display_results()
        self.setup_signals()

    def setup_signals(self):
        self.pushButtonWritePrevious.clicked.connect(self.go_to_previous)

    def go_to_previous(self):
        if self.parent() is not None:
            self.parent().show()
            self.hide()
        else:
            QMessageBox.warning(self, "Error", "Cannot go back: Previous page not found!")

    def display_results(self):
        if self.results_df.empty:
            QMessageBox.warning(self, "Error", "No search results found!")
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

        name_font = QFont("Georgia", 16, QFont.Weight.Bold)
        other_font = QFont("Georgia", 14)
        # Load photo
        photos_df = load_photos_from_mysql()
        if photos_df is not None and 'business_id' in self.results_df.columns:
            self.results_df = self.results_df.merge(photos_df[['photo_id', 'business_id']], on='business_id',
                                                    how='left')
            print("Results_df after merge with photos:")
            print(self.results_df)
        names = self.results_df['name'].tolist()
        locations = self.results_df['location'].tolist()
        categories = self.results_df['categories'].tolist()
        ratings = self.results_df['bs_rating'].tolist()
        photo_ids = self.results_df['photo_id'].tolist() if 'photo_id' in self.results_df.columns else [None] * len(
            self.results_df)
        print(f"Number of results: {len(self.results_df)}")
        print(f"Names: {names}")

        for i in range(10):
            if i < len(names):
                name = str(names[i]).strip('"') if pd.notna(names[i]) else "N/A"
                location = str(locations[i]).strip('"') if pd.notna(locations[i]) else "N/A"
                category = str(categories[i]).strip('"') if pd.notna(categories[i]) else "N/A"
                rating = str(ratings[i]).strip('"') if pd.notna(ratings[i]) else "Not rated"
                label_names[i].setText(name)
                label_names[i].setFont(name_font)
                label_locations[i].setText(location)
                label_locations[i].setFont(other_font)
                label_categories[i].setText(category)
                label_categories[i].setFont(other_font)
                label_ratings[i].setText(rating)
                label_ratings[i].setFont(other_font)
                figure_labels[i].setScaledContents(True)
                if pd.notna(photo_ids[i]):
                    photo_path = os.path.join(photos_folder, f"{photo_ids[i]}.jpg")
                    if os.path.exists(photo_path):
                        pixmap = QPixmap(photo_path)
                        figure_labels[i].setPixmap(pixmap)
                    else:
                        figure_labels[i].setText("No image available")
                else:
                    figure_labels[i].setText("No image available")
            else:
                label_names[i].setText("")
                label_locations[i].setText("")
                label_categories[i].setText("")
                label_ratings[i].setText("")
                figure_labels[i].setText("")

    def showWindow(self):
        self.show()
