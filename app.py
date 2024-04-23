import os
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, request, redirect, session, jsonify
from random import shuffle
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'

deck_lock = threading.Lock()
deck = list(range(1, 53))
shuffle(deck)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    name = request.form['name']
    session['name'] = name
    session['cards'] = []  # Initialize cards for the session
    return redirect('/game')

@app.route('/game')
def game():
    return render_template('game.html')

@app.route('/draw')
def draw_card():
    with deck_lock:
        if deck:
            card = deck.pop()
            if 'cards' not in session:
                session['cards'] = []  # Ensure session card list is initialized
            session['cards'].append(card)
            session.modified = True
            return jsonify({'card': card, 'remaining': len(deck)})
        else:
            return jsonify({'error': 'No cards left'}), 400

@app.route('/shuffle')
def shuffle_deck():
    with deck_lock:
        deck[:] = list(range(1, 53))
        shuffle(deck)
    session['cards'] = []  # Clear the session cards on reshuffle
    session.modified = True
    return jsonify({'message': 'Deck reshuffled', 'remaining': len(deck)})

@app.route('/show')
def show_cards():
    return jsonify({'cards': session.get('cards', [])})

if __name__ == '__main__':
    # Corrected to use environment variable for port
    port = int(os.getenv('PORT', 5000))  # Default to 5000 if no PORT variable is set
    http_server = WSGIServer(('0.0.0.0', port), app)
    http_server.serve_forever()
