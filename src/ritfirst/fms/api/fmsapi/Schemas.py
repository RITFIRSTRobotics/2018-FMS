from marshmallow import Schema, fields

from ritfirst.fms.appl.game.MatchTimeThread import MatchTimeThread
from ritfirst.fms.appl.RobotNetworkService import RobotNetworkService
from ritfirst.fms.appl.game.GameService import GameService
from ritfirst.fms.appl.game.ScoringService import ScoringService
from ritfirst.fms.api.fmsapi.ScoreboardModel import ScoreboardModel

class MatchTimeThreadSchema(Schema):
    remaining = fields.Integer()

class RobotNetworkServiceSchema(Schema):
    disabled = fields.Boolean()

class ScoringServiceSchema(Schema):
    red_score = fields.Integer()
    blue_score = fields.Integer()

class GameServiceSchema(Schema):
    match_thread = fields.Nested(MatchTimeThreadSchema)
    match_running = fields.Boolean()
    r_net_service = fields.Nested(RobotNetworkServiceSchema)
    scoring_service = fields.Nested(ScoringServiceSchema)

class ScoreboardModelSchema(Schema):
    game_service = fields.Nested(GameServiceSchema)
