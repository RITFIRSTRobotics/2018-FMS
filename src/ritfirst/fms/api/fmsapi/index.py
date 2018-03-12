from flask import Flask, jsonify, request
from ritfirst.fms.api.fmsapi.StatusModel import StatusModel
from ritfirst.fms.api.fmsapi.ScoreboardModel import ScoreboardModel

app = Flask(__name__)

bots = [
    { 'id': 1, 'description': 'pusher bot 1'},
    { 'id': 2, 'description': 'pusher bot 2'}
]

status = StatusModel()
scoreboard = ScoreboardModel()

@app.route('/game/init')
def init_game():
    return scoreboard.game_service, 200

@app.route('/game/start')
def start_game():
    return scoreboard.start_match()

@app.route('/game/stop')
def stop_game():
    return scoreboard.stop_match()

@app.route('/game/timer')
def game_timer():
    return scoreboard.get_remaining_time()

@app.route('/game/scores')
def game_scores():
    return scoreboard.get_scores()

@app.route('/ports')
def get_ports():
    code, data = status.check_ports()
    if code != 0:
        return data
    else:
        return jsonify({i:str(port) for i, port in enumerate(data)})

@app.route('/bots')
def get_bots():
    return jsonify(bots)

@app.route('/bots', methods=['POST'])
def add_bot():
    bots.append(request.get_json())
    return '', 204