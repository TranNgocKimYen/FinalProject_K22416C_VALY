import pickle
import os
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import RegexpTokenizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
def stem_and_tokenize(list_):
    pattern = r"(?u)\b\w\w+\b"
    tokenizer = RegexpTokenizer(pattern)
    stemmer = SnowballStemmer(language="english")
    tokens = tokenizer.tokenize(list_)
    return [stemmer.stem(token) for token in tokens]
def create_features(data):
    import nltk; nltk.download('stopwords')
    stopwords_list = stopwords.words('english')
    stopwords_list = [SnowballStemmer(language="english").stem(i) for i in stopwords_list]
    tfidf = TfidfVectorizer(max_features=200, stop_words=stopwords_list, tokenizer=stem_and_tokenize)
    tfidf_matrix = tfidf.fit_transform(data['details'])
    cosine_sim = cosine_similarity(tfidf_matrix)
    os.makedirs('./data', exist_ok=True)
    pickle.dump(tfidf_matrix, open('./data/tfidf_matrix.pkl', 'wb'))
    pickle.dump(cosine_sim, open('./data/cosine_similarity.pkl', 'wb'))
    pickle.dump(data, open('./data/data.pkl', 'wb'))
    return tfidf_matrix, cosine_sim, data
def load_features():
    with open('.ml/data/preprocessed/cosine_similarity.pkl', 'rb') as file: cosine_similarity = pickle.load(file)
    with open('./data/data.pkl', 'rb') as file: df = pickle.load(file)
    return cosine_similarity, df
    