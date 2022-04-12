import os

import pandas as pd
import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from surprise import Dataset, Reader, accuracy, SVD
from surprise.model_selection import train_test_split
import sys


def _prepare_data():
    movies = pd.read_csv('data/movies.csv')
    tags = pd.read_csv('data/tags.csv')
    ratings = pd.read_csv('data/ratings.csv')

    movie_list_rating = ratings.movieId.unique().tolist()
    movies = movies[movies.movieId.isin(movie_list_rating)]

    # map movie to id
    mapping = dict(zip(movies.title.tolist(), movies.movieId.tolist()))
    # remove timestamps
    tags.drop(['timestamp'], axis=1, inplace=True)
    ratings.drop(['timestamp'], axis=1, inplace=True)
    # merge dfs
    mixed = pd.merge(movies, tags, on='movieId', how='left')

    # create metadata from all tags and genres
    mixed.fillna("", inplace=True)
    mixed = pd.DataFrame(mixed.groupby('movieId')['tag'].apply(lambda x: "%s" % ' '.join(x)))
    final = pd.merge(movies, mixed, on='movieId', how='left')
    final['metadata'] = final[['tag', 'genres']].apply(lambda x: ' '.join(x), axis=1)

    # text transformation and truncated SVD to create a content latent matrix
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(final['metadata'])
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), index=final.index.tolist())
    svd = TruncatedSVD(n_components=200)
    latent_matrix_1 = svd.fit_transform(tfidf_df)
    latent_matrix_1_df = pd.DataFrame(
                             latent_matrix_1,
                             index=final.title.tolist())

    # text transformation and truncated SVD to create a collaborative latent matrix
    ratings_1 = pd.merge(movies['movieId'], ratings, on="movieId", how="right")
    ratings_2 = ratings_1.pivot(index='movieId', columns='userId',
                                values='rating').fillna(0)
    svd = TruncatedSVD(n_components=200)
    latent_matrix_2 = svd.fit_transform(ratings_2)
    latent_matrix_2_df = pd.DataFrame(latent_matrix_2,
                                      index=final.title.tolist())

    return {
        'ratings_1': ratings_1,
        'ratings': ratings,
        'latent_matrix_1_df': latent_matrix_1_df,
        'latent_matrix_2_df': latent_matrix_2_df,
        'mapping': mapping,
    }


def _save_model(data):
    if not os.path.exists('model'):
        os.mkdir('model')
    data['ratings'].to_pickle('model/rating.pkl')
    data['latent_matrix_1_df'].to_pickle('model/latent_content.pkl')
    data['latent_matrix_2_df'].to_pickle('model/latent_collaborative.pkl')
    with open('model/map.pkl', 'wb') as f:
        pickle.dump(data['mapping'], f, pickle.HIGHEST_PROTOCOL)
    with open('model/model_svd.pkl', 'wb') as f:
        pickle.dump(data['algo'], f, pickle.HIGHEST_PROTOCOL)


def model_is_trained():
    return True if os.path.exists('model/model_svd.pkl') else False


def train_model():
    data = _prepare_data()

    # train user collaborative model using Surprise
    reader = Reader(rating_scale=(1, 5))
    dataset = Dataset.load_from_df(data['ratings_1'][['userId', 'movieId', 'rating']], reader)
    trainset, testset = train_test_split(dataset, test_size=.25)

    algorithm = SVD(n_factors=200, n_epochs=50)
    algorithm.fit(trainset)
    accuracy.rmse(algorithm.test(testset))

    data['algo'] = algorithm
    _save_model(data)


if __name__ == "__main__":
    train_model()

