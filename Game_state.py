class GameState:
    def __init__(self):
        self.vertical_walls = set()
        self.horizontal_walls = set()
        self.first_player_pos = [4, 0]
        self.second_player_pos = [4, 8]
        self.first_player_walls = 10
        self.second_player_walls = 10
        self.first_player_turn = True
        self.move_log = []
        self.redo_moves = []
        self.winner = ""

    def move(self, pos):
        if self.first_player_turn:
            self.move_log.append(["move", self.first_player_pos])
            self.first_player_pos = pos
        else:
            self.move_log.append(["move", self.second_player_pos])
            self.second_player_pos = pos
        self.first_player_turn = not self.first_player_turn
        self.redo_moves.clear()

    def place_wall(self, pos, orientation):
        if self.first_player_turn:
            self.first_player_walls -= 1
        else:
            self.second_player_walls -= 1
        if orientation == "horizontal_wall":
            self.horizontal_walls.add(pos)
            self.move_log.append(["horizontal", pos])
        elif orientation == "vertical_wall":
            self.vertical_walls.add(pos)
            self.move_log.append(["vertical", pos])
        self.first_player_turn = not self.first_player_turn

    def undo(self):
        if not self.move_log:
            return
        self.first_player_turn = not self.first_player_turn
        last_move = self.move_log[-1]
        move_type = last_move[0]
        pos = last_move[1]
        if move_type == "move":
            if self.first_player_turn:
                self.redo_moves.append([move_type, self.first_player_pos])
                self.first_player_pos = pos
            else:
                self.redo_moves.append([move_type, self.second_player_pos])
                self.second_player_pos = pos
        elif move_type in ["horizontal", "vertical"]:
            if self.first_player_turn:
                self.first_player_walls += 1
            else:
                self.second_player_walls += 1
            if move_type == "horizontal":
                self.horizontal_walls.remove(pos)
            elif move_type == "vertical":
                self.vertical_walls.remove(pos)
            self.redo_moves.append([move_type, pos])
        self.move_log.pop()

    def redo(self):
        if not self.redo_moves:
            return
        last_move = self.redo_moves[-1]
        move_type = last_move[0]
        pos = last_move[1]
        if move_type == "move":
            if self.first_player_turn:
                self.move_log.append(["move", self.first_player_pos])
                self.first_player_pos = pos
            else:
                self.move_log.append(["move", self.second_player_pos])
                self.second_player_pos = pos
        elif move_type in ["horizontal", "vertical"]:
            if self.first_player_turn:
                self.first_player_walls -= 1
            else:
                self.second_player_walls -= 1
            if move_type == "horizontal":
                self.horizontal_walls.add(pos)
            elif move_type == "vertical":
                self.vertical_walls.add(pos)
            self.move_log.append([move_type, pos])
        self.first_player_turn = not self.first_player_turn
        self.redo_moves.pop()
