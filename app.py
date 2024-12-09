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

def generate_random_number():
    """Generate a random number for the game."""
    return random.randint(1, 100)

@app.route('/', methods=['GET', 'POST'])
def index():
    """Welcome page."""
    if request.method == 'POST':
        if request.form.get('start_game') == 'Start Game':
            session.clear()  # Clear session data when starting a new game
            session['username'] = request.form.get('username', f"User_{random.randint(1000, 9999)}")
            return redirect('/game')
    return render_template("index.html")

@app.route('/game', methods=['GET', 'POST'])
def game():
    """Main game logic."""
    if 'score' not in session:
        session['score'] = 0
        session['number1'] = generate_random_number()
        session['number2'] = generate_random_number()

    while session['number1'] == session['number2']:
        session['number2'] = generate_random_number()

    if request.method == 'POST':
        user_guess = request.form.get('guess')
        number1 = session['number1']
        number2 = session['number2']

        correct_guess = "higher" if number2 > number1 else "lower"

        if user_guess == correct_guess:
            session['score'] += 1
        else:
            # Update Redis leaderboard before showing Game Over and set highscore
            username = session['username']
            stored_score = redis_client.zscore(LEADERBOARD_KEY, username)
            if stored_score is None or session['score'] > stored_score:
                redis_client.zadd(LEADERBOARD_KEY, {username: session['score']})
            return redirect('/game_over')

        # Generate new numbers
        session['number1'] = generate_random_number()
        session['number2'] = generate_random_number()

    return render_template(
        'game.html',
        number1=session['number1'],
        number2=session['number2'],
        score=session['score']
    )

@app.route('/game_over', methods=['GET', 'POST'])
def game_over():
    """Game over page."""
    if request.method == 'POST':
        # Reset session for a new game
        session['score'] = 0
        session['number1'] = generate_random_number()
        session['number2'] = generate_random_number()
        return redirect('/game')

    return render_template('game_over.html', score=session['score'])

@app.route('/leaderboard')
def leaderboard():
    """Display the leaderboard."""
    top_players = redis_client.zrevrange(LEADERBOARD_KEY, 0, 9, withscores=True)
    return render_template('leaderboard.html', top_players=top_players)

if __name__ == '__main__':
    app.run(debug=True)
