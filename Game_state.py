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
        available_moves = self.check_movement()
        if tuple(pos) not in available_moves:
            return
        if self.first_player_turn:
            self.move_log.append(["move", self.first_player_pos])
            self.first_player_pos = pos
            self.winner = "first_player" if pos[1] == 8 else self.winner
        else:
            self.move_log.append(["move", self.second_player_pos])
            self.second_player_pos = pos
            self.winner = "second_player" if pos[1] == 0 else self.winner
        self.first_player_turn = not self.first_player_turn
        self.redo_moves.clear()

    def place_wall(self, pos, orientation):
        if not self.can_place_wall(pos, orientation):
            return
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

    def is_in_bounds(self, pos):
        return 0 <= pos[0] < 9 and 0 <= pos[1] < 9

    def is_wall_blocking(self, pos, dx, dy, wall_type):
        if wall_type == 'V':
            dx = dx if dx == 1 else 0
            return (pos[0] - dx, pos[1]) in self.vertical_walls or (pos[0] - dx, pos[1] - 1) in self.vertical_walls
        elif wall_type == 'H':
            dy = dy if dy == 1 else 0
            return (pos[0], pos[1] - dy) in self.horizontal_walls or (pos[0] - 1, pos[1] - dy) in self.horizontal_walls

    def check_movement(self):
        available_moves = []
        player_pos = tuple(self.first_player_pos if self.first_player_turn else self.second_player_pos)
        opponent_pos = tuple(self.second_player_pos if self.first_player_turn else self.first_player_pos)
        offsets = [
            (0, 1, 'H'),  # Down
            (0, -1, 'H'),  # Up
            (1, 0, 'V'),  # right
            (-1, 0, 'V')  # Left
        ]
        for dx, dy, wall_type in offsets:
            target_pos = (player_pos[0] + dx, player_pos[1] + dy)
            if not self.is_in_bounds(target_pos) or self.is_wall_blocking(target_pos, dx, dy, wall_type):
                continue
            if target_pos == opponent_pos:
                new_target_pos = (target_pos[0] + dx, target_pos[1] + dy)
                if self.is_in_bounds(new_target_pos) and not self.is_wall_blocking(new_target_pos, dx, dy, wall_type):
                    available_moves.append(new_target_pos)
                elif self.is_wall_blocking(new_target_pos, dx, dy, wall_type):
                    diagonals = [(0, 1, 'H'), (0, -1, 'H')] if wall_type == 'V' else [(1, 0, 'V'), (-1, 0, 'V')]
                    for ddx, ddy, dwall_type in diagonals:
                        diagonal_pos = (target_pos[0] + ddx, target_pos[1] + ddy)
                        if self.is_in_bounds(diagonal_pos) and not self.is_wall_blocking(diagonal_pos, ddx, ddy,
                                                                                         dwall_type):
                            available_moves.append(diagonal_pos)
            else:
                available_moves.append(target_pos)
        return available_moves

    def get_neighbors(self, pos):
        neighbors = []
        offsets = [
            (0, 1, 'H'),  # Down
            (0, -1, 'H'),  # Up
            (1, 0, 'V'),  # right
            (-1, 0, 'V')  # Left
        ]
        for dx, dy, wall_type in offsets:
            target_pos = (pos[0] + dx, pos[1] + dy)
            if not self.is_in_bounds(target_pos) or self.is_wall_blocking(target_pos, dx, dy, wall_type):
                continue
            neighbors.append(target_pos)

        return neighbors

    def clear_path(self, player_name):
        if player_name == "first_player":
            start_pos = tuple(self.first_player_pos)
            winning_row = 8
        elif player_name == "second_player":
            start_pos = tuple(self.second_player_pos)
            winning_row = 0

        queue = [start_pos]
        visited = {start_pos}

        while queue:
            current = queue.pop()
            if current[1] == winning_row:
                return True
            neighbors = self.get_neighbors(current)
            for neighbor in neighbors:
                if neighbor not in visited:
                    queue.append(neighbor)
                    visited.add(neighbor)
        return False

    def can_place_wall(self, pos, orientation):
        if orientation == "horizontal_wall":
            if pos in self.horizontal_walls or (pos[0] + 1, pos[1]) in self.horizontal_walls or (
                    pos[0] - 1, pos[1]) in self.horizontal_walls or pos in self.vertical_walls:
                return False
            self.horizontal_walls.add(pos)
        elif orientation == "vertical_wall":
            if pos in self.vertical_walls or (pos[0], pos[1] - 1) in self.vertical_walls or (
                    pos[0], pos[1] + 1) in self.vertical_walls or pos in self.horizontal_walls:
                return False
            self.vertical_walls.add(pos)

        first_player_path = self.clear_path("first_player")
        second_player_path = self.clear_path("second_player")

        if orientation == "horizontal_wall":
            self.horizontal_walls.remove(pos)
        elif orientation == "vertical_wall":
            self.vertical_walls.remove(pos)

        return first_player_path and second_player_path
