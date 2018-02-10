from flask import Flask, jsonify, request

app = Flask(__name__)

bots = [
    { 'id': 1, 'description': 'pusher bot 1'}
]

@app.route('/bots')
def get_bots():
    return jsonify(bots)

@app.route('/bots', methods=['POST'])
def add_bot():
    bots.append(request.get_json())
    return '', 204