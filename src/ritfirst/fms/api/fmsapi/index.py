from flask import Flask, jsonify, request
from ritfirst.fms.api.fmsapi.StatusModel import StatusModel
from ritfirst.fms.api.fmsapi.ScoreboardModel import ScoreboardModel
from ritfirst.fms.api.fmsapi.Schemas import ScoreboardModelSchema, GameServiceSchema

app = Flask(__name__)

bots = [
    { 'id': 1, 'description': 'pusher bot 1'},
    { 'id': 2, 'description': 'pusher bot 2'}
]

status = StatusModel()
scoreboard = ScoreboardModel()

@app.route('/game/init')
def init_game():
    return ScoreboardModelSchema().dumps(scoreboard).data, 200

@app.route('/game/start')
def start_game():
    game_state, http_code = scoreboard.start_match()
    return GameServiceSchema().dumps(game_state).data, http_code

@app.route('/game/stop')
def stop_game():
    game_state, http_code = scoreboard.stop_match()
    return GameServiceSchema().dumps(game_state).data, http_code

@app.route('/game/timer')
def game_timer():
    timer, http_code = scoreboard.get_remaining_time()
    return jsonify({'remaining': timer}), http_code

@app.route('/game/scores')
def game_scores():
    scores, http_code = scoreboard.get_scores()
    return jsonify({'red_score': scores[0], 'blue_score': scores[1]}), http_code

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