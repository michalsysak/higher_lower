from flask import Flask, render_template, request, redirect, url_for
import redis
import random
import os
from dotenv import load_dotenv
import uuid
import runpy

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "default_secret_key")  # Secure this key in production
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_KEY_PREFIX'] = 'tab_session:'
app.config['SECRET_KEY'] = 'your_secret_key'

# Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Constants
LEADERBOARD_KEY = "higher_lower:leaderboard"
TIMEOUT = 3600  # Session timeout in seconds
TAB_SESSION_KEY = "tab_session:{}"  # Key pattern for tab-specific data

# Global movie list
movies = []

# Utility functions

#FOR DEVELOPMENT ONLY
def init():
    redis_client.flushall()
    runpy.run_path("helpers/load_movies_to_redis.py")
    load_movie_data_from_redis()

def load_movie_data_from_redis():
    """Load movie data from Redis."""
    movie_keys = redis_client.keys("movie:*")
    for redis_key in movie_keys:
        movie_data = redis_client.hgetall(redis_key)
        movie_data["vote_average"] = float(movie_data["vote_average"])
        movie_data["vote_count"] = int(movie_data["vote_count"])
        movies.append(movie_data)

def pick_random_movie():
    """Pick a random movie."""
    return random.choice(movies)

def get_tab_data(tab_id):
    """Retrieve tab-specific data from Redis."""
    tab_key = TAB_SESSION_KEY.format(tab_id)
    tab_data = redis_client.hgetall(tab_key)
    if tab_data:
        if 'movie1' in tab_data:
            tab_data['movie1'] = eval(tab_data['movie1'])  # Or use `json.loads` if JSON is used
        if 'movie2' in tab_data:
            tab_data['movie2'] = eval(tab_data['movie2'])
        if 'score' in tab_data:
            tab_data['score'] = int(tab_data['score'])
        if 'game_over' in tab_data:
            tab_data['game_over'] = tab_data['game_over'] == 'True'
    return tab_data

def save_tab_data(tab_id, data):
    """Save tab-specific data to Redis."""
    tab_key = TAB_SESSION_KEY.format(tab_id)
    redis_client.hset(tab_key, mapping={
        'username': data['username'],
        'score': data.get('score', 0),
        'game_over': str(data.get('game_over', False)),
        'movie1': str(data['movie1']),
        'movie2': str(data['movie2']),
    })
    redis_client.expire(tab_key, TIMEOUT)  # Set expiration for tab session


# Load movie data
#load_movie_data_from_redis()
init()

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    """Welcome page."""

    if request.method == 'POST':
        if request.form.get('start_game') == 'Start Game':
            username = request.form.get('username').strip()

            tab_id = str(uuid.uuid4())  # Generate unique tab ID

            # Initialize tab-specific data in Redis
            save_tab_data(tab_id, {
                'username': username,
                'score': 0,
                'game_over': False,
                'movie1': pick_random_movie(),
                'movie2': pick_random_movie()
            })

            return redirect(url_for('game', tab_id=tab_id))
    return render_template("index.html")

@app.route('/game/<tab_id>', methods=['GET', 'POST'])
def game(tab_id):
    """Main game logic."""
    # Validate tab_id
    if not tab_id:
        return redirect(url_for('index'))

    # Retrieve tab-specific data
    tab_data = get_tab_data(tab_id)

    if tab_data['game_over']:
        return redirect(url_for('game_over'))

    # Ensure movies are different
    while tab_data['movie1']['id'] == tab_data['movie2']['id']:
        tab_data['movie2'] = pick_random_movie()

    if request.method == 'POST':
        user_guess = request.form.get('guess')

        # Calculate movie scores
        movie1_score = float(tab_data['movie1']['vote_average']) * int(tab_data['movie1']['vote_count'])
        movie2_score = float(tab_data['movie2']['vote_average']) * int(tab_data['movie2']['vote_count'])
        correct_guess = "lower" if movie2_score > movie1_score else "higher"

        if user_guess == correct_guess:
            tab_data['score'] += 1
        else:
            tab_data['game_over'] = True
            save_tab_data(tab_id, tab_data)

            # Update leaderboard
            username = tab_data['username']
            stored_score = redis_client.zscore(LEADERBOARD_KEY, username)
            if stored_score is None or tab_data['score'] > stored_score:
                redis_client.zadd(LEADERBOARD_KEY, {username: tab_data['score']})

            return redirect(url_for('game_over', tab_id=tab_id))

        # Generate new movies
        tab_data['movie1'] = pick_random_movie()
        tab_data['movie2'] = pick_random_movie()

        # Save updated data
        save_tab_data(tab_id, tab_data)

    return render_template(
        'game.html',
        movie1=tab_data['movie1'],
        movie2=tab_data['movie2'],
        score=tab_data['score'],
        username=tab_data['username']
    )


@app.route('/game_over/<tab_id>', methods=['GET', 'POST'])
def game_over(tab_id):
    """Game over page."""
    # Retrieve tab-specific data
    tab_data = get_tab_data(tab_id)
    if not tab_data:
        return redirect(url_for('index'))

    if request.method == 'POST':
        # Reset game data for a new game session
        tab_data.update({
            'score': 0,
            'game_over': False,
            'movie1': pick_random_movie(),
            'movie2': pick_random_movie()
        })
        save_tab_data(tab_id, tab_data)
        return redirect(url_for('game', tab_id=tab_id))

    return render_template('game_over.html', username=tab_data['username'], score=tab_data['score'])


@app.route('/leaderboard')
def leaderboard():
    """Display the leaderboard."""
    top_players = redis_client.zrevrange(LEADERBOARD_KEY, 0, 9, withscores=True)
    return render_template('leaderboard.html', top_players=top_players)

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
