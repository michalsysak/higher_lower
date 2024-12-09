from flask import Flask, render_template, request, session, redirect
import redis
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # Secure this key in production

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Constants
LEADERBOARD_KEY = "higher_lower:leaderboard"


movies = []

def load_movie_data_from_redis():
    """Load the movie data from redis db"""
    movie_keys = redis_client.keys("movie:*")
    # Fetch data and store in a list
    for redis_key in movie_keys:
        movie_data = redis_client.hgetall(redis_key)

        # Convert numeric fields back to integers or floats
        movie_data["vote_average"] = float(movie_data["vote_average"])
        movie_data["vote_count"] = int(movie_data["vote_count"])

        movies.append(movie_data)

load_movie_data_from_redis()

def pick_random_movie():
    """Pick a random movie"""
    return random.choice(movies)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Welcome page."""
    if request.method == 'POST':
        if request.form.get('start_game') == 'Start Game':
            session.clear()  # Clear session data when starting a new game
            session['username'] = request.form.get('username', f"User_{random.randint(1000, 9999)}")#TODO add that 2 users dont get the same id
            return redirect('/game')
    return render_template("index.html")

@app.route('/game', methods=['GET', 'POST'])
def game():
    """Main game logic."""
    session['game_over']=False
    if 'score' not in session:
        # Assign the score and set the movie parameters
        session['score'] = 0
        session['movie1'] = pick_random_movie()
        session['movie2'] = pick_random_movie()

    # Pick another movie until there are 2 different movies
    while session['movie1']['id'] == session['movie2']['id']:
        session['movie2'] = pick_random_movie()

    if request.method == 'POST':
        user_guess = request.form.get('guess')
        # Calculate the scores
        movie1_score = session['movie1']['vote_average'] * session['movie1']['vote_count']
        movie2_score = session['movie2']['vote_average'] * session['movie2']['vote_count']

        print(f"{session['movie1']['title']}: {movie1_score} | {session['movie2']['title']}: {movie2_score}")

        correct_guess = "lower" if movie2_score > movie1_score else "higher"

        if user_guess == correct_guess:
            session['score'] += 1
        else:
            # Update Redis leaderboard before showing Game Over and set highscore
            session['game_over'] = True
            username = session['username']
            stored_score = redis_client.zscore(LEADERBOARD_KEY, username)
            if stored_score is None or session['score'] > stored_score:
                redis_client.zadd(LEADERBOARD_KEY, {username: session['score']})
            return redirect('/game_over')

        # Generate new movies
        session['movie1'] = pick_random_movie()
        session['movie2'] = pick_random_movie()

    return render_template(
        'game.html',
        movie1=session['movie1'],
        movie2=session['movie2'],
        score=session['score']
    )

@app.route('/game_over', methods=['GET', 'POST'])
def game_over():
    """Game over page."""
    if request.method == 'POST':
        # Reset session for a new game
        session['score'] = 0
        # Load new movies
        session['movie1'] = pick_random_movie()
        session['movie2'] = pick_random_movie()
        return redirect('/game')

    return render_template('game_over.html', score=session['score'])

@app.route('/leaderboard')
def leaderboard():
    """Display the leaderboard."""
    top_players = redis_client.zrevrange(LEADERBOARD_KEY, 0, 9, withscores=True)
    if session['game_over']:
        # Load new movies
        session['movie1'] = pick_random_movie()
        session['movie2'] = pick_random_movie()
    return render_template('leaderboard.html', top_players=top_players)

if __name__ == '__main__':
    app.run(debug=True)
