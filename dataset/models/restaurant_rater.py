import pandas as pd
def restaurant_rater(data, num=10, location=None, category=None):
    """
    This function retrieves the list of restaurants to display on the interface.
    The user enters a review and submits it once.
    """
    df_restaurant = data.copy()
    if df_restaurant.empty:
        return pd.DataFrame()
    # Select the list of restaurants based on the given conditions.
    if location:
        restaurants = df_restaurant[df_restaurant['location'].str.contains(location, case=False, na=False)].sample(
            min(num, len(df_restaurant)))
    elif category:
        restaurants = df_restaurant[df_restaurant['categories'].str.contains(category, case=False, na=False)].sample(
            min(num, len(df_restaurant)))
    else:
        restaurants = df_restaurant.sample(min(num, len(df_restaurant)))
    # Create a column `user_rating` to store user reviews.
    restaurants["user_rating"] = None
    restaurants.to_csv("restaurants.csv", index=False)
    return restaurants