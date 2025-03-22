import folium
import pandas as pd
from PIL._imaging import display
from nltk.corpus import stopwords
from ml.features import stem_and_tokenize, load_features
from ml.data.data import load_data



def folium_map(data):
    dff = data.reset_index(drop=True)
    center_lat = dff['latitude'][0]
    center_long = dff['longitude'][0]
    map_ = folium.Map([center_lat, center_long], zoom_start=7)
    limit = dff.shape[0]
    print(f"{limit-1} Restaurant Locations")
    for index in range(limit-1):
        lat = dff.loc[index, 'latitude']
        long = dff.loc[index, 'longitude']
        name = dff.loc[index, 'name']
        rating = dff.loc[index, 'bs_rating']
        location = dff.loc[index, 'location']
        details = "{}\\nStars: {} {}".format(name, rating, location)
        popup = folium.Popup(details, parse_html=True)
        marker = folium.Marker(location=[lat, long], popup=popup)
        marker.add_to(map_)
    return display(map_)

cosine_similarity, df = load_features()
def content_based(name=None, rating=1, num=5, text=None, location=None):
    if name:
        index_ = df.loc[df.name == name].index[0]
        sim = list(enumerate(cosine_similarity[index_]))
        sim = sorted(sim, key=lambda x: x[1], reverse=True)[1:num+1]
        indices = [i[0] for i in sim]
        print(f"Top {num} Restaurants Like [{name}]")
        if location:
            df = df.loc[(df['bs_rating']>=rating) & (df.location.str.contains(location))]
            folium_map(df)
        else:
            df = df.loc[df['bs_rating']>=rating]
        df = df.loc[indices,('name','bs_rating','review_count','location')].sort_values('bs_rating', ascending=False)
        return df.reset_index(drop=True)
    else:
        if text:
            text = text.lower()
            tokens = stem_and_tokenize(text)
            tokens = [word for word in tokens if word not in stopwords]
            text_set = set(tokens)
            if location:
                df = df.loc[(df.location.str.contains(location)) & (df['bs_rating']>=rating)].reset_index(drop=True)
            vectors = []
            for words in df.details:
                words = words.lower()
                words = stem_and_tokenize(words)
                words = [word for word in words if word not in stopwords]
                words = set(words)
                vector = text_set.intersection(words)
                vectors.append(len(vector))
            vectors = sorted(list(enumerate(vectors)), key=lambda x: x[1], reverse=True)[:num]
            indices = [i[0] for i in vectors]
            print(f"Top {num} Best Restaurants Based on entered text:")
            df = df.loc[indices].sort_values(by=['bs_rating','review_count'],ascending=False)
            if location: folium_map(df)
            return df[['name','bs_rating','review_count','location']].reset_index(drop=True)
        if location:
            df = df.loc[df.location.str.contains(location)& (df['bs_rating']>=rating)]
            df = df.sort_values(['review_count','bs_rating'])[:num]
            folium_map(data=df)
            return df[['name','bs_rating','review_count','location']].reset_index(drop=True)
        else:
            df = df.loc[df['bs_rating']>=rating].sort_values(by=['review_count','bs_rating'],ascending=False)[:num]
            if location: folium_map(data=df)
            print("Most Popular Restaurants")
            return df[['name','bs_rating','review_count','location']].reset_index(drop=True)