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
        # If the moove is invalid, return False
        available_moves = self.check_movement()
        if tuple(pos) not in available_moves:
            return False

        # If the move is valid, move the turn player to that position and then log that move in the move_log
        if self.first_player_turn:
            self.move_log.append(["move", self.first_player_pos])
            self.first_player_pos = pos
            self.winner = "first_player" if pos[1] == 8 else self.winner
        else:
            self.move_log.append(["move", self.second_player_pos])
            self.second_player_pos = pos
            self.winner = "second_player" if pos[1] == 0 else self.winner

        # Finally, switch the turn to the other player and return True
        self.first_player_turn = not self.first_player_turn
        return True

    def place_wall(self, pos, orientation):
        # If the moove is invalid, return False
        if not self.can_place_wall(pos, orientation):
            return False

        # If the move is valid, subtract the wall from the player's wall storage
        if self.first_player_turn:
            self.first_player_walls -= 1
        else:
            self.second_player_walls -= 1

        # Place the wall in it's position and in the set it belongs to, depending on it's orientation
        if orientation == "horizontal_wall":
            self.horizontal_walls.add(pos)
            self.move_log.append(["horizontal", pos])
        elif orientation == "vertical_wall":
            self.vertical_walls.add(pos)
            self.move_log.append(["vertical", pos])

        # Finally, log the move in the move_log and return true
        self.first_player_turn = not self.first_player_turn
        return True

    def undo(self, store_undo):
        """If the store_undo is True, this function stores the move it undid in the redo queue"""

        # If the move log is empty, do nothing
        if not self.move_log:
            return

        # Switch to the previous player first and then see the last move
        self.first_player_turn = not self.first_player_turn
        last_move = self.move_log[-1]
        move_type = last_move[0]
        pos = last_move[1]

        # Determine the type of the move and undo it
        if move_type == "move":
            if self.first_player_turn:
                if store_undo:
                    self.redo_moves.append([move_type, self.first_player_pos])
                self.first_player_pos = pos
            else:
                if store_undo:
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
            if store_undo:
                self.redo_moves.append([move_type, pos])
        self.move_log.pop()
        self.winner = ""

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
                self.winner = "first_player" if pos[1] == 8 else ""
            else:
                self.move_log.append(["move", self.second_player_pos])
                self.second_player_pos = pos
                self.winner = "second_player" if pos[1] == 0 else ""
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
        """This function checks if a cell is blocked from another cell by a wall"""
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

            # check for every adjacent cell if it's blocked by a wall or out of the bounds of the board
            target_pos = (player_pos[0] + dx, player_pos[1] + dy)
            if not self.is_in_bounds(target_pos) or self.is_wall_blocking(target_pos, dx, dy, wall_type):
                continue

            # Check if the adjacent cell contains the opponent
            if target_pos == opponent_pos:

                # If there is an opponent, check if the cell behind them is not blocked and is inbounds
                new_target_pos = (target_pos[0] + dx, target_pos[1] + dy)
                if self.is_in_bounds(new_target_pos) and not self.is_wall_blocking(new_target_pos, dx, dy, wall_type):
                    available_moves.append(new_target_pos)

                # if the cell behind them is blocked, check the diagonal cells and add them if they aren't blocked
                elif self.is_wall_blocking(new_target_pos, dx, dy, wall_type):
                    diagonals = [(0, 1, 'H'), (0, -1, 'H')] if wall_type == 'V' else [(1, 0, 'V'), (-1, 0, 'V')]
                    for ddx, ddy, dwall_type in diagonals:
                        diagonal_pos = (target_pos[0] + ddx, target_pos[1] + ddy)
                        if self.is_in_bounds(diagonal_pos) and not self.is_wall_blocking(diagonal_pos, ddx, ddy,
                                                                                         dwall_type):
                            available_moves.append(diagonal_pos)

            # If the opponent doesn't occupy the adjacent cell, add it to the list
            else:
                available_moves.append(target_pos)

        return available_moves

    def get_neighbors(self, pos):
        """This function returns the available adjacent cells to a certain cell"""

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

    def shortest_path(self, start_pos, winning_row):
        """This function uses Breadth-first search to find the shortest path from the start position to the winning row
         and returns false if it didn't find a path"""

        queue = [[start_pos]]
        visited = {start_pos}

        while queue:
            current_path = queue.pop(0)
            current_cell = current_path[-1]

            if current_cell[1] == winning_row:
                return current_path
            neighbors = self.get_neighbors(current_cell)
            for neighbor in neighbors:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(list(current_path) + [neighbor])
        return False

    def can_place_wall(self, pos, orientation):
        """This function checks if a wall placement is legal"""
        player_walls = self.first_player_walls if self.first_player_turn else self.second_player_walls

        # Check if the wall crosses or overlaps other walls
        if orientation == "horizontal_wall":
            if pos in self.horizontal_walls or (pos[0] + 1, pos[1]) in self.horizontal_walls or (
                    pos[0] - 1, pos[1]) in self.horizontal_walls or pos in self.vertical_walls or player_walls <= 0:
                return False

            # Add the wall temporarily to see if there is a path for both players to their winning rows
            self.horizontal_walls.add(pos)

        elif orientation == "vertical_wall":
            if pos in self.vertical_walls or (pos[0], pos[1] - 1) in self.vertical_walls or (
                    pos[0], pos[1] + 1) in self.vertical_walls or pos in self.horizontal_walls or player_walls <= 0:
                return False

            # Add the wall temporarily to see if there is a path for both players to their winning rows
            self.vertical_walls.add(pos)

        # Apply BFS to know if both players have a path to victory
        if not self.shortest_path(tuple(self.first_player_pos), 8):
            if orientation == "horizontal_wall":
                self.horizontal_walls.remove(pos)
            elif orientation == "vertical_wall":
                self.vertical_walls.remove(pos)
            return False  # Short-circuit exit

        if orientation == "horizontal_wall":
            self.horizontal_walls.remove(pos)
        elif orientation == "vertical_wall":
            self.vertical_walls.remove(pos)
        return bool(self.shortest_path(tuple(self.second_player_pos), 0))

    def get_all_wall_moves(self):
        all_legal_wall_moves = []

        # These inner loops generate all possible wall moves and check which of them is a legal move
        for i in range(8):
            for j in range(8):
                for orientation in ['vertical_wall', 'horizontal_wall']:
                    if self.can_place_wall((i, j), orientation):
                        all_legal_wall_moves.append([(i, j), orientation])
        return all_legal_wall_moves
