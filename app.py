import os
from gevent.pywsgi import WSGIServer
from flask import Flask, render_template, request, redirect, session, jsonify, url_for
from random import shuffle
import threading

app = Flask(__name__)
app.secret_key = 'your_secret_key'

deck_lock = threading.Lock()
deck = list(range(1, 53))
shuffle(deck)

def card_filename(card_number):
    suits = ['clubs', 'diamonds', 'hearts', 'spades']
    values = ['ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'jack', 'queen', 'king']
    if card_number < 1 or card_number > 52:
        return None
    suit = suits[(card_number - 1) // 13]
    value = values[(card_number - 1) % 13]
    filename = f"AllCardImages/{value}_of_{suit}.svg"  # Include the subfolder in the path
    return filename

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
            card_number = deck.pop()
            card_img_url = url_for('static', filename=card_filename(card_number))
            if 'cards' not in session:
                session['cards'] = []  # Ensure session card list is initialized
            session['cards'].append(card_number)
            session.modified = True
            return jsonify({'card': card_number, 'remaining': len(deck), 'card_img_url': card_img_url})
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
