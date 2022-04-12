# Recommender System MovieLens 100k
A movie recommender system based on movie-lens database served with a Flask-restful app.
This recommendation system uses the concepts of both memory and model based filtering to make top N recommendations.

You can make different types of requests which will take you to different endpoints. In the directory of Recommender-movie, run the API locally: > python app.py.
## Installation
Change your directory to project directory and build docker image
```
docker build -t recsys:latest .
```
Run container
```
docker run -d -p 5000:5000 recsys
```

## Usage
Basic example for user-based recommendation of movies that user did not rated before would be the following command:
```
curl -X GET http://127.0.0.1:5000/recommend -d user_id=x -d limit=n
```
where x is id of a user (should be in dataset), n is limitation on movies in response.

Response example:
```
{
    "result": [
        "Amelie (Fabuleux destin d'Am\u00e9lie Poulain, Le) (2001)",
        "Schindler's List (1993)",
        "Casablanca (1942)",
        "Lone Star (1996)",
        "Eternal Sunshine of the Spotless Mind (2004)",
        "2001: A Space Odyssey (1968)",
        "Jaws (1975)",
        "Little Big Man (1970)",
        "Eraserhead (1977)",
        "Shining, The (1980)"
    ]
}
```
To test this result on intersection with already rated movies you can use /test endpoint:
```
curl -X POST http://127.0.0.1:5000/test -d user_id=x
```

Another possibility is to get top n movies, similar to a particular movie via content, collaborative or hybrid filtering:
```
curl -X POST http://127.0.0.1:5000/movies/[basis] -d movie=[movie] -d limit=n
```
where [basis] can be content, collaborative or hybrid, [movie] is the name of a movie in the database, n is an integer.

Example:
```
curl -X POST http://127.0.0.1:5000/movies/collaborative -d movie="Inception (2010)" -d limit=10
```
Response:
```
{
    "collaborative": [
        "Shutter Island (2010)",
        "Inglourious Basterds (2009)",
        "Avatar (2009)",
        "Social Network, The (2010)",
        "District 9 (2009)",
        "Black Swan (2010)",
        "Sherlock Holmes (2009)",
        "Kick-Ass (2010)",
        "King's Speech, The (2010)",
        "Up (2009)"
    ]
}
```

















