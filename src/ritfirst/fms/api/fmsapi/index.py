from flask import Flask, jsonify, request
from ritfirst.fms.api.fmsapi.ScoreboardModel import ScoreboardModel
from ritfirst.fms.api.fmsapi.Schemas import ScoreboardModelSchema, GameServiceSchema

def create_flask_app():
    app = Flask(__name__)

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

    return app