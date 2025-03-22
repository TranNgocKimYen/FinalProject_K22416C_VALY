# FinalProject_K22416C_VALY
 
## Introduction
This is a restaurant recommendation system built using the Yelp Open Dataset. It employs techniques such as TF-IDF, Cosine Similarity, and SVD to analyze user reviews and provide tailored recommendations.

## Directory Structure
- **dataset/**: Contains preprocessed data and related resources, including:
  - `.pkl` files after feature engineering, such as:
    - Cosine similarity matrix (https://drive.google.com/file/d/19jtlbnUgUIzuVucaEtOgL6GkNTpXdb9V/view?usp=sharing)
    - TF-IDF matrix (https://drive.google.com/file/d/1Wo_AhE0HjKNh74ow6QMjEqPj0FX0RUC0/view?usp=sharing)
    - Processed dataset
  - **models/**: Subdirectory storing compressed formats of trained machine learning models (e.g., `svdmodel.zip`).
  - **raw_data/**: Holds the original collected data, consisting of two JSON files:
    - `business.json`
    - `review.json`
  - **photos/**: Contains `.png` files representing image data of businesses (restaurants) in the dataset. Due to the large size of the image data, it has been compressed. To use the `photos` directory, download it from [this link](https://drive.google.com/file/d/1mpyu2LLZVU1fuTV0fdJLpbL_LvMUlG3Q/view?usp=sharing), then extract and place it into the `dataset/` directory.

- **Images/**: This directory (at the same level as `dataset/`) contains images used for designing the user interface and displaying them on the interface during operation.

- **libs/**: This directory (at the same level as `dataset/`) stores functions for connecting to a MySQL database. These functions are designed to connect to different tables, retrieve data from the database, and save data back to it.

- **UI/**: This directory (at the same level as `dataset/`) contains `.ui` files (interface design files) and `.py` files that enable interaction between users and the interface. It also integrates the machine learning model with the designed interface.

- **Test/**: This file or directory (at the same level as `dataset/`) is used to test-run the recommendation system.
