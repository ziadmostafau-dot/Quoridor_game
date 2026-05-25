import pygame
from Game_state import GameState
from support import *
from Engine import *


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Quoridor')
        self.clock = pygame.time.Clock()
        self.running = True
        self.gs = GameState()
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        self.phase = "neutral"
        self.mode = "human"
        self.menu = True

    def draw_board(self, game_state):
        # Draw cells
        for row in range(9):
            for col in range(9):
                pygame.draw.rect(self.display_surface, FG_COLOR, ((SQUARE_SIZE + WALL_THICKNESS) * col,
                                                                  (SQUARE_SIZE + WALL_THICKNESS) * row,
                                                                  SQUARE_SIZE, SQUARE_SIZE))

            # Draw players
            x_pos = (SQUARE_SIZE + WALL_THICKNESS) * game_state.first_player_pos[0] + SQUARE_SIZE / 2
            y_pos = (SQUARE_SIZE + WALL_THICKNESS) * game_state.first_player_pos[1] + SQUARE_SIZE / 2
            pygame.draw.circle(self.display_surface, FP_COLOR, (x_pos, y_pos), SQUARE_SIZE / 2)
            x_pos = (SQUARE_SIZE + WALL_THICKNESS) * game_state.second_player_pos[0] + SQUARE_SIZE / 2
            y_pos = (SQUARE_SIZE + WALL_THICKNESS) * game_state.second_player_pos[1] + SQUARE_SIZE / 2
            pygame.draw.circle(self.display_surface, SP_COLOR, (x_pos, y_pos), SQUARE_SIZE / 2)

        # Draw walls between cells
        for pos in game_state.vertical_walls:
            x_pos = SQUARE_SIZE + (SQUARE_SIZE + WALL_THICKNESS) * pos[0]
            y_pos = (SQUARE_SIZE + WALL_THICKNESS) * pos[1]
            pygame.draw.rect(self.display_surface, WALL_COLOR,
                             (x_pos, y_pos, WALL_THICKNESS, 2 * SQUARE_SIZE + WALL_THICKNESS))

        for pos in game_state.horizontal_walls:
            x_pos = (SQUARE_SIZE + WALL_THICKNESS) * pos[0]
            y_pos = SQUARE_SIZE + (SQUARE_SIZE + WALL_THICKNESS) * pos[1]
            pygame.draw.rect(self.display_surface, WALL_COLOR, (x_pos, y_pos, 2 * SQUARE_SIZE + WALL_THICKNESS,
                                                                WALL_THICKNESS))

    def draw_game_information(self, game_state):
        # Draw whose turn it is
        turn_text = "Red player" if game_state.first_player_turn else "Blue player"
        self.display_surface.blit(self.font.render(f"{turn_text}'s turn", True, FONT_COLOR),
                                  ((SQUARE_SIZE + WALL_THICKNESS) * 9, 0))

        # Draw first player's wall count
        self.display_surface.blit(
            self.font.render(f"Red player: {game_state.first_player_walls} walls", True, FONT_COLOR),
            ((SQUARE_SIZE + WALL_THICKNESS) * 9, 100))

        # Draw second player's wall count
        self.display_surface.blit(
            self.font.render(f"Blue player: {game_state.second_player_walls} walls", True, FONT_COLOR),
            ((SQUARE_SIZE + WALL_THICKNESS) * 9, 150))

        # Draw who is the winner
        if game_state.winner == "first_player":
            winner_text = " Winner is: Red player"
        elif game_state.winner == "second_player":
            winner_text = "Winner is: Blue player"
        else:
            winner_text = ""
        self.display_surface.blit(
            self.font.render(winner_text, True, FONT_COLOR),
            ((SQUARE_SIZE + WALL_THICKNESS) * 9, 200))

        # Draw the option to place horizontal walls
        pygame.draw.rect(self.display_surface, FG_COLOR, ((SQUARE_SIZE + WALL_THICKNESS) * 9, 300, 300, 50))
        self.display_surface.blit(self.font.render("Place horizontal wall", True, FONT_COLOR),
                                  ((SQUARE_SIZE + WALL_THICKNESS) * 9, 312))

        # Draw the option to place vertical walls
        pygame.draw.rect(self.display_surface, FG_COLOR, ((SQUARE_SIZE + WALL_THICKNESS) * 9, 400, 300, 50))
        self.display_surface.blit(self.font.render("Place vertical wall", True, FONT_COLOR),
                                  ((SQUARE_SIZE + WALL_THICKNESS) * 9, 412))

    def draw_highlighting(self, game_state):
        x_position, y_position = pygame.mouse.get_pos()
        x_position = x_position // (SQUARE_SIZE + WALL_THICKNESS)
        x_position = 7 if x_position > 7 else x_position  # Make x_position stay in board
        y_position = y_position // (SQUARE_SIZE + WALL_THICKNESS)
        y_position = 7 if y_position > 7 else y_position  # Make y_position stay in board

        # Highlight vertical wall placement
        if self.phase == "vertical_wall":
            # see if the wall placement is valid, if it's not, give the highlighting a different color
            color = WALL_HIGHLIGHT if game_state.can_place_wall((x_position, y_position),
                                                                "vertical_wall") else INVALID_WALL
            x_position = x_position * (SQUARE_SIZE + WALL_THICKNESS) + SQUARE_SIZE
            y_position *= (SQUARE_SIZE + WALL_THICKNESS)
            pygame.draw.rect(self.display_surface, color,
                             (x_position, y_position, WALL_THICKNESS, 2 * SQUARE_SIZE + WALL_THICKNESS))

        # Highlight horizontal wall placement
        elif self.phase == "horizontal_wall":
            # see if the wall placement is valid, if it's not, give the highlighting a different color
            color = WALL_HIGHLIGHT if game_state.can_place_wall((x_position, y_position),
                                                                "horizontal_wall") else INVALID_WALL
            x_position *= (SQUARE_SIZE + WALL_THICKNESS)
            y_position = y_position * (SQUARE_SIZE + WALL_THICKNESS) + SQUARE_SIZE
            pygame.draw.rect(self.display_surface, color,
                             (x_position, y_position, 2 * SQUARE_SIZE + WALL_THICKNESS, WALL_THICKNESS))

        # Highlight valid pawn moves
        elif self.phase == "neutral":
            highlighted_squares = game_state.check_movement()
            for square in highlighted_squares:
                pygame.draw.rect(self.display_surface, SQUARE_HIGHLIGHT, ((SQUARE_SIZE + WALL_THICKNESS) * square[0],
                                                                          (SQUARE_SIZE + WALL_THICKNESS) * square[1],
                                                                          SQUARE_SIZE, SQUARE_SIZE))

    def draw_menu(self):
        pos = (SQUARE_SIZE + WALL_THICKNESS) * 3
        pygame.draw.rect(self.display_surface, BG_COLOR, (50, pos - 50, 450, 300))
        self.display_surface.blit(self.font.render("Select mode:", True, FONT_COLOR), (60, pos - 40))
        y = 0
        text = ["Human vs human", "Human vs AI: Easy mode", "Human vs AI: Medium mode", "Human vs AI: Hard mode"]
        for i in range(4):
            pygame.draw.rect(self.display_surface, FG_COLOR, (60, pos + y, 430, 50))
            self.display_surface.blit(self.font.render(text[i], True, FONT_COLOR),
                                      (60, pos + 10 + y))
            y += (SQUARE_SIZE + WALL_THICKNESS)

    def draw_game(self, game_state):
        self.draw_board(game_state)
        self.draw_game_information(game_state)
        self.draw_highlighting(game_state)
        if self.menu:
            self.draw_menu()

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # Check if there is no winner yet
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.gs.winner == "":
                    # Get coordinates of clicked cell
                    x_coord = event.pos[0] // (SQUARE_SIZE + WALL_THICKNESS)
                    y_coord = event.pos[1] // (SQUARE_SIZE + WALL_THICKNESS)

                    # Select the game mode (Human or AI)
                    if self.menu and 1 <= x_coord < 8 and 3 <= y_coord < 7:
                        modes = ["human", "easy", "medium", "hard"]
                        self.mode = modes[y_coord - 3]
                        self.menu = False
                    else:
                        # check if the coordinates are inside the board and if the player is trying to move a pawn
                        if x_coord < 9 and y_coord < 9 and self.phase == "neutral":
                            made_move = self.gs.move([x_coord, y_coord])

                            # If the move is valid, delete the redo history
                            if made_move:
                                self.gs.redo_moves.clear()

                            # If the opponent is an AI, get the action that the AI suggests
                            if self.mode != "human" and made_move and self.gs.winner == "":
                                action = AI(self.gs, self.mode)

                                # See if the action is to place a wall or move a pawn, and then execute it
                                if action[1] == "horizontal_wall" or action[1] == "vertical_wall":
                                    self.gs.place_wall(action[0], action[1])
                                else:
                                    self.gs.move(action)

                        # Check if the player pressed on the "Place a horizontal wall" textbox
                        elif 9 <= x_coord < 14 and y_coord == 5:

                            # If the horizontal wall movement is already toggled on, toggle back to pawn movement
                            if self.phase == "horizontal_wall":
                                self.phase = "neutral"

                            # else, check if the player has walls in storage, if yes, go to the horizontal
                            # wall placement phase
                            elif (self.gs.first_player_turn and self.gs.first_player_walls > 0) or (
                                    (not self.gs.first_player_turn) and self.gs.second_player_walls > 0):
                                self.phase = "horizontal_wall"

                        # Check if the player pressed on the "Place a horizontal wall" textbox
                        elif 9 <= x_coord < 14 and y_coord == 7:

                            # If the vertical wall movement is already toggled on, toggle back to pawn movement
                            if self.phase == "vertical_wall":
                                self.phase = "neutral"

                            # else, check if the player has walls in storage, if yes, go to the vertical
                            # wall placement phase
                            elif (self.gs.first_player_turn and self.gs.first_player_walls > 0) or (
                                    (not self.gs.first_player_turn) and self.gs.second_player_walls > 0):
                                self.phase = "vertical_wall"

                        # If the player is already placing a wall and clicked on the screen:
                        elif self.phase in ["horizontal_wall", "vertical_wall"]:

                            # limit the coordinates of the mouse click to inside the board
                            x_coord = 7 if x_coord > 7 else x_coord
                            y_coord = 7 if y_coord > 7 else y_coord

                            # Make the wall placement
                            made_move = self.gs.place_wall((x_coord, y_coord), self.phase)

                            # If the wall placement is valid, delete redo history
                            if made_move:
                                self.gs.redo_moves.clear()

                            # If the move is valid and the opponent is an AI, make the AI make a move
                            if made_move and self.mode != "human" and self.gs.winner == "":
                                action = AI(self.gs, self.mode)
                                if action[1] == "horizontal_wall" or action[1] == "vertical_wall":
                                    self.gs.place_wall(action[0], action[1])
                                else:
                                    self.gs.move(action)

                            # Return back to pawn movement phase
                            self.phase = "neutral"

                elif event.type == pygame.KEYDOWN:
                    # If the player pressed u, undo the last move and store it in the redo queue
                    if event.key == pygame.K_u:
                        self.gs.undo(True)

                        # If the opponent is an AI, undo the movement again and store it in the redo queue
                        if self.mode != "human":
                            self.gs.undo(True)

                        # After the undo, return back to pawn movement phase
                        self.phase = "neutral"

                    # If the player pressed r, redo the last move
                    elif event.key == pygame.K_r:
                        self.gs.redo()

                        # If the opponent is an AI, redo the movement
                        if self.mode != "human":
                            self.gs.redo()

                        # After the redo, return back to pawn movement phase
                        self.phase = "neutral"

                    # If the player pressed q, reset the entire game and reinitialize the game_state object
                    elif event.key == pygame.K_q:
                        self.gs.__init__()

                        # After resetting, go back pawn movement phase
                        self.phase = "neutral"

            # draw
            self.display_surface.fill(BG_COLOR)
            self.draw_game(self.gs)
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
