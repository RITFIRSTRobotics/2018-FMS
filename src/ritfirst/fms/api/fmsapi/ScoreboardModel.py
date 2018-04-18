class ScoreboardModel:
    game_service = None

    def __init__(self, game_service):
        self.game_service = game_service
        pass

    def start_match(self):
        if self.game_service.match_running == False:
#            self.game_service.start_match()
            return self.game_service, 200
        else:
            return self.game_service, 304

    def stop_match(self):
        if self.game_service.match_running == True:
#            self.game_service.stop_match() this line was causing matches to randomly stop
            return self.game_service, 200
        else:
            return self.game_service, 304

    def get_scores(self):
        return self.game_service.get_scores(), 200
    
    def get_remaining_time(self):
        return self.game_service.get_remaining_time(), 200
