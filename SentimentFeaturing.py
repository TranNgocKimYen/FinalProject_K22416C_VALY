import os
import mysql.connector
import pandas as pd
import pickle
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Phydy@1311",
    database="restaurant_rs",
    charset="utf8mb4",
    port=8000)
cursor = conn.cursor()

# Query data from MySQL
query = "SELECT * FROM reviews;"
cursor.execute(query)
# Convert data to DataFrame
columns = [desc[0] for desc in cursor.description]
dataset = cursor.fetchall()
data = pd.DataFrame(dataset, columns=columns)
# Close connection
cursor.close()
conn.close()

def new_df(x):
    """
    The function takes in a dataframes and groups it by business_id column then combines all the text values in the
    text column into one big text then assigns it to the review column

    """
    # drop duplicates based on business_id and reset the index
    df = x.drop_duplicates('business_id').reset_index(drop=True)
    # loop through unique business_id values
    for id in x.business_id.unique():
        # extract text for each unique business_id and explode it into separate rows
        text = x.loc[x.business_id == id, 'text'].explode(ignore_index=True)
        # join the exploded text into a single string
        text = ' '.join(text)
        # assign the concatenated text to the reviews column for the corresponding business_id
        df.loc[x.business_id == id, 'reviews'] = text

    return df

df = new_df(data)
df.head()


# decompressing the attributes column into  new 'attributes_true' column
def decompress(x):
    """
    The function takes in a dictionary and returns only the keys that have their values not being False
    """
    list_ = []
    # evaluate the attributes column to convert it from a string to a dictionary
    data_dict = eval(x)

    # iterate through the key-value pairs in the dictionary
    for key, val in data_dict.items():
        # check if the key is in the specified categories and if the value is not "None"
        if (key in ['Ambience', 'GoodForMeal', 'BusinessParking']) and (val != "None"):
            # if conditions are met, further iterate through sub-dictionary
            for key_, val_ in eval(data_dict[key]).items():
                # if the sub-dictionary value is true, append it to the list
                if val_:
                    list_.append(f'{key}_{key_}')
        else:
            # if the value is not false, append the key to the list
            if val != 'False':
                list_.append(key)

    # join the list of selected attribute names into a space-separated string
    return " ".join(list_)
# create a new column 'attributes_true' in the df by applying the decompress function
df['attributes_true'] = df.attributes.apply(lambda x: decompress(x) if x != 'Not-Available' else ' ')

# confirming if the newly created column has performed as expected
print("Before:")
print(eval(df.attributes[0]))
print('\n After:')
df['attributes_true'][0]

# merging different columns to form one column of text
df['details'] = df[['attributes_true', 'categories', 'reviews']].apply(lambda x: ''.join(x), axis=1)

# previewing the first row value in the new column
df.details[0]
# dropping columns
df.drop(columns=['attributes_true', 'reviews'], inplace=True)
# first create a pattern that strips all the non-word characters from words during tokenization
pattern = r"(?u)\b\w\w+\b"

# instantiate the tokenizer
tokenizer = RegexpTokenizer(pattern)

# instantiating the stemmer
stemmer = SnowballStemmer(language="english")


# creating a function to tokenize and stem words
def stem_and_tokenize(list_):
    tokens = tokenizer.tokenize(list_)
    return [stemmer.stem(token) for token in tokens]

#nltk.download('stopwords')

# instantiating the stop words
stopwords=stopwords.words('english')
# stemming the stopwords for uniformity while removing stopwords
stopwords=[ stemmer.stem(i) for i in stopwords]


tfidf = TfidfVectorizer( max_features=200 ,
                        stop_words=stopwords,
                        tokenizer= stem_and_tokenize
#                         ngram_range=(1, 2),
#                         min_df=0,
                        )
# fitting and transforming the details column to extract the top 200 features
tfidf_matrix=tfidf.fit_transform(df['details'])

# previewing the tfidf matrix
pd.DataFrame.sparse.from_spmatrix(tfidf_matrix, columns=tfidf.get_feature_names_out()).head()

tfidf_df = pd.DataFrame.sparse.from_spmatrix(tfidf_matrix, columns=tfidf.get_feature_names_out())
print(tfidf_df.head())

# creating a matrix of the cosine similarities of the various rows based on the tidf scores
cosine_similarity=cosine_similarity(tfidf_matrix)
print("shape: ",cosine_similarity.shape)

# viewing the first column
cosine_similarity[0]
os.makedirs('./dataset', exist_ok=True)
pickle.dump(tfidf_matrix, open('./dataset/tfidf_matrix.pkl', 'wb'))
# saving our data for deployment
pickle.dump(cosine_similarity, open('./dataset/cosine_similarity.pkl', 'wb'))
pickle.dump(df, open('./dataset/data.pkl', 'wb'))
print("Files saved...")
# Print the result for the first row of 'attributes'
with open('./dataset/cosine_similarity.pkl', 'rb') as file:
    cosine_similarity = pickle.load(file)

with open('./dataset/data.pkl', 'rb') as file:
    df = pickle.load(file)

