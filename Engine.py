import random


def shortest_immediate_path(game_state):
    """This function checks all available pawn moves to the AI and returns the shortest path"""

    available_moves = game_state.check_movement()
    shortest_path = None
    length = 1000
    for move in available_moves:
        path = game_state.shortest_path(move, 0)
        if len(path) < length:
            shortest_path = path
            length = len(path)
    return shortest_path


def easy_mode(game_state):
    """This algorithm makes a random wall placement
     20% of the time and takes the shortest path 80% of the time"""

    roll = random.random()
    if roll < 0.2:
        all_legal_wall_moves = game_state.get_all_wall_moves()
        if all_legal_wall_moves:
            random_move = random.choice(all_legal_wall_moves)
            return random_move

        # If there are no legal wall moves, take the shortest path instead
        shortest_path = shortest_immediate_path(game_state)
        return shortest_path[0]

    shortest_path = shortest_immediate_path(game_state)
    return shortest_path[0]


def medium_mode(games_state):
    """This algorithm performs a minmax algorithm with a depth of 1"""

    all_wall_moves = games_state.get_all_wall_moves()
    all_pawn_moves = games_state.check_movement()
    score = -1000
    action = None
    if all_wall_moves:
        for pos, orientation in all_wall_moves:
            if orientation == "horizontal_wall":
                games_state.horizontal_walls.add(pos)
            elif orientation == "vertical_wall":
                games_state.vertical_walls.add(pos)
            human_score = len(games_state.shortest_path(tuple(games_state.first_player_pos), 8))
            ai_score = len(games_state.shortest_path(tuple(games_state.second_player_pos), 0))
            current_score = human_score - ai_score
            if orientation == "horizontal_wall":
                games_state.horizontal_walls.remove(pos)
            elif orientation == "vertical_wall":
                games_state.vertical_walls.remove(pos)

            if current_score > score:
                score = current_score
                action = [pos, orientation]
    for pos in all_pawn_moves:
        temp = games_state.second_player_pos
        games_state.second_player_pos = pos
        human_score = len(games_state.shortest_path(tuple(games_state.first_player_pos), 8))
        ai_score = len(games_state.shortest_path(tuple(games_state.second_player_pos), 0))
        current_score = human_score - ai_score
        games_state.second_player_pos = temp

        if current_score >= score:
            score = current_score
            action = pos
    return action


def get_filtered_wall_moves(state):
    """Generates potential wall coordinates near player paths without heavy validation."""
    human_path = state.shortest_path(tuple(state.first_player_pos), 8)
    ai_path = state.shortest_path(tuple(state.second_player_pos), 0)

    if not human_path or not ai_path:
        return []

    # Focus strictly on tiles the players are actively using
    active_tiles = set(human_path) | set(ai_path)
    filtered_moves = []

    # Tight 1-tile radius around the paths for high-impact walls
    for i in range(8):
        for j in range(8):
            # checks all adjacent and diagonal tiles to the active_tiles
            if any(abs(i - tx) <= 1 and abs(j - ty) <= 1 for tx, ty in active_tiles):
                # We do NOT run BFS checks here.
                # Minimax will filter out illegal ones automatically via place_wall()
                filtered_moves.append([(i, j), 'vertical_wall'])
                filtered_moves.append([(i, j), 'horizontal_wall'])
    return filtered_moves


def hard_mode(games_state, depth=2):
    best_score = -float('inf')
    best_action = None

    all_pawn_moves = games_state.check_movement()
    all_wall_moves = get_filtered_wall_moves(games_state)

    # Calculate the ideal next step to break pawn oscillation ties
    current_ai_path = games_state.shortest_path(tuple(games_state.second_player_pos), 0)
    ideal_next_step = tuple(current_ai_path[1]) if (current_ai_path and len(current_ai_path) > 1) else None

    # 1. EVALUATE PAWNS
    for pos in all_pawn_moves:
        games_state.move(pos)
        score = alpha_beta_minimax(games_state, depth - 1, -float('inf'), float('inf'), False)
        games_state.undo(False)

        # Tie-breaker nudge: If this move marches along our ideal path, favor it
        if ideal_next_step and tuple(pos) == ideal_next_step:
            score += 0.1

        if score > best_score:
            best_score = score
            best_action = pos

    # 2. EVALUATE WALLS
    if games_state.second_player_walls > 0:
        for pos, orientation in all_wall_moves:
            # place_wall safely returns False if illegal, skipping deep BFS calculations completely
            if games_state.place_wall(pos, orientation):
                score = alpha_beta_minimax(games_state, depth - 1, -float('inf'), float('inf'), False)
                games_state.undo(False)

                if score > best_score:
                    best_score = score
                    best_action = [pos, orientation]

    return best_action


def alpha_beta_minimax(state, depth, alpha, beta, is_maximizing):
    if depth == 0 or state.winner != "":
        human_path = state.shortest_path(tuple(state.first_player_pos), 8)
        ai_path = state.shortest_path(tuple(state.second_player_pos), 0)

        if human_path is False or ai_path is False:
            return -1000 if is_maximizing else 1000

        return len(human_path) - len(ai_path)

    if is_maximizing:
        max_eval = -float('inf')

        # Track ideal step for tie-breaking inside the tree
        current_path = state.shortest_path(tuple(state.second_player_pos), 0)
        ideal_step = tuple(current_path[1]) if (current_path and len(current_path) > 1) else None

        for move in state.check_movement():
            state.move(list(move))
            evaluation = alpha_beta_minimax(state, depth - 1, alpha, beta, False)
            state.undo(False)

            if ideal_step and tuple(move) == ideal_step:
                evaluation += 0.1

            max_eval = max(max_eval, evaluation)
            alpha = max(alpha, evaluation)
            if beta <= alpha:
                return max_eval

        if state.second_player_walls > 0:
            for pos, orientation in get_filtered_wall_moves(state):
                if state.place_wall(pos, orientation):
                    evaluation = alpha_beta_minimax(state, depth - 1, alpha, beta, False)
                    state.undo(False)
                    max_eval = max(max_eval, evaluation)
                    alpha = max(alpha, evaluation)
                    if beta <= alpha:
                        return max_eval
        return max_eval

    else:
        min_eval = float('inf')

        current_path = state.shortest_path(tuple(state.first_player_pos), 8)
        ideal_step = tuple(current_path[1]) if (current_path and len(current_path) > 1) else None

        for move in state.check_movement():
            state.move(list(move))
            evaluation = alpha_beta_minimax(state, depth - 1, alpha, beta, True)
            state.undo(False)

            if ideal_step and tuple(move) == ideal_step:
                evaluation -= 0.1  # Human wants to minimize AI's score advantage

            min_eval = min(min_eval, evaluation)
            beta = min(beta, evaluation)
            if beta <= alpha:
                return min_eval

        if state.first_player_walls > 0:
            for pos, orientation in get_filtered_wall_moves(state):
                if state.place_wall(pos, orientation):
                    evaluation = alpha_beta_minimax(state, depth - 1, alpha, beta, True)
                    state.undo(False)
                    min_eval = min(min_eval, evaluation)
                    beta = min(beta, evaluation)
                    if beta <= alpha:
                        return min_eval
        return min_eval


def AI(game_state, difficulty):
    if difficulty == "easy":
        return easy_mode(game_state)
    elif difficulty == "medium":
        return medium_mode(game_state)
    elif difficulty == "hard":
        return hard_mode(game_state, 2)
