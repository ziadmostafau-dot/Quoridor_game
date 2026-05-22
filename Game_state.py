class GameState:
    def __init__(self):
        self.vertical_walls = set()
        self.horizontal_walls = set()
        self.first_player_pos = [0, 4]
        self.second_player_pos = [8, 4]
        self.first_player_walls = 10
        self.second_player_walls = 10
        self.first_player_turn = True
        self.move_log = []
        self.winner = ""
