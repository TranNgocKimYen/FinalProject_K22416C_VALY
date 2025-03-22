import pandas as pd
from joblib import load

def cf_model(df, num=10, location=None, name=None, text=None, model_path=r'C:\Users\OS\LAVY\LAVY_FINALPROJECT\dataset\models\svdmodel.zip'):
    """
    The function takes the following inputs;

    df: DataFrame - a dataframe containing unique restaurants
    name: str - name of restaurant to recommend similar restaurants
    num: int - number of restaurants to recommend
    location: string - preferred location
    text: - User preferences in form of text
    model_path: str - path to the pre-trained SVD model file (default: 'svdmodel.zip')

    The function loads a pre-trained SVD model and uses it to predict and recommend restaurants based on user ratings.
    """
    df = df.drop_duplicates(subset=['business_id']).copy()
    user_ratings = df[df['user_rating'].notna()].copy()
    if user_ratings.empty:
        print("No user ratings found!")
        return pd.DataFrame()

    user_ratings = user_ratings.drop_duplicates(subset=['business_id'])
    df['rating'] = df['user_rating'].combine_first(df['bs_rating'])
    df = pd.concat([df, user_ratings], axis=0, ignore_index=True)
    df = df.drop_duplicates(subset=['business_id'])
    #Load the SVD model from the compressed file.
    svd = load(model_path)
    user_id = user_ratings['user_id'].values[0] if not user_ratings.empty else 'default_user'
    if location:
        df = df.loc[df['location'].str.contains(location, case=False, na=False)]

    unique_business_ids = df['business_id'].unique()
    if len(unique_business_ids) < num:
        print(
            f"Warning: Only {len(unique_business_ids)} unique business IDs available, but {num} recommendations requested.")
        num = len(unique_business_ids)
    user_predictions = []
    for iid in unique_business_ids:
        pred = svd.predict(user_id, iid)
        user_predictions.append((iid, pred.est))
    # Sort the predictions in descending order by score.
    top_pred = sorted(user_predictions, key=lambda x: x[1], reverse=True)
    # Retrieve the top *num* recommended restaurants.
    indices = [i[0] for i in top_pred[:num]]
    rec = df.loc[df['business_id'].isin(indices)].sort_values('bs_rating', ascending=False)
    rec = rec.drop_duplicates(subset=['business_id'])

    if len(rec) < num:
        remaining = num - len(rec)
        additional_ids = df[~df['business_id'].isin(indices)]['business_id'].sample(n=remaining, replace=False)
        additional_recs = df.loc[df['business_id'].isin(additional_ids)]
        rec = pd.concat([rec, additional_recs], ignore_index=True).head(num)

    return rec[['business_id', 'name', 'categories', 'bs_rating', 'location']].reset_index(drop=True)

