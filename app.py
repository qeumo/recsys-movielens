import pandas as pd
from flask import Flask, request
from flask_restful import Resource, Api, reqparse
import pickle
import numpy as np
from model import ContentBased, CollabBased, HybridBased, ModelBased
from train_model import train_model, model_is_trained


# the recommender module
class Recommender:

    def __init__(self):
        if not model_is_trained():
            print('Training model...')
            train_model()
            print('Model is trained')

        with open('model/model_svd.pkl', 'rb') as f:
            self.algo = pickle.load(f)
        with open('model/map.pkl', 'rb') as f:
            self.movie_map = pickle.load(f)
        with open('model/rating.pkl', 'rb') as f:
            self.rating = pickle.load(f)
        with open('model/latent_collaborative.pkl', 'rb') as f:
            latent_collab = pickle.load(f)
        with open('model/latent_content.pkl', 'rb') as f:
            latent_content = pickle.load(f)

        self.clf_content = ContentBased(latent_content)
        self.clf_collab = CollabBased(latent_collab)
        self.clf_hybrid = HybridBased(latent_content, latent_collab)
        self.clf_algo = ModelBased(self.algo)

    def parsing_args(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('movie', required=False,
                                 help="movie title followed by year")
        self.parser.add_argument('limit', required=False,
                                 help="N in top N films")

    def get_all_recommendations(self, movie_name, n):
        if movie_name in self.movie_map.keys():

            output = {
                'content': {'content':
                            self.clf_content.predict_top_n(movie_name, n)},
                'collaborative': {'collaborative':
                                  self.clf_collab.predict_top_n(movie_name, n)},
                'hybrid': {'hybrid':
                           self.clf_hybrid.predict_top_n(movie_name, n)},
                }
        else:
            output = f"Invalid movie name. Try another, ex: '{next(iter(self.movie_map))}'"
        return output

    def get_user_recommendation(self, user_id, n):
        if not check_positive(n):
            output = "Erorr. 'limit' should be positive integer"

        elif check_positive(user_id) and int(user_id) in self.rating.userId.unique():
            ui_list = self.rating[self.rating.userId == int(user_id)].movieId.tolist()
            d = {k: v for k, v in self.movie_map.items() if v not in ui_list}
            output = self.clf_algo.predict_top_n_user(int(user_id), d, int(n))
        else:
            output = f"Invalid user id. Try another, ex: {self.rating.userId[0]}"
        return output


# the app
app = Flask(__name__)
api = Api(app)


def check_positive(n):
    try:
        if int(n) > 0:
            return True
    except:
        pass

    return False


class MovieBasis(Resource):

    def post(self, basis):
        result = {}
        movie = request.form['movie']
        n = request.form['limit'] if 'limit' in request.form else 10
        output = ex.get_all_recommendations(movie, n)

        result['result'] = output[basis]

        return result


class UserBasis(Resource):

    def post(self):
        result = {}
        n = request.form['limit'] if 'limit' in request.form else 10
        user_id = request.form['user_id']
        output = ex.get_user_recommendation(user_id, n)

        result['result'] = output

        return result


class TestRecommend(Resource):
    def post(self):
        n = request.form['limit'] if 'limit' in request.form else 10
        user_id = request.form['user_id']
        output = ex.get_user_recommendation(user_id, n)

        movies = pd.read_csv('data/movies.csv')
        ratings = pd.read_csv('data/ratings.csv')
        sel = pd.merge(ratings[ratings.userId == user_id], movies[['movieId', 'title']], on='movieId')
        assert sel.title.isin(output).sum() == 0

        return True


api.add_resource(MovieBasis, '/movies/<basis>')
api.add_resource(UserBasis, '/recommend')
api.add_resource(TestRecommend, '/test')

if __name__ == '__main__':
    ex = Recommender()
    ex.parsing_args()
    app.run(host='0.0.0.0', debug=True, port=5000)

