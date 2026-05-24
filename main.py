import pygame

from Game_state import GameState
from support import *


class Game:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Quoridor')
        self.clock = pygame.time.Clock()
        self.running = True
        self.gs = GameState()
        self.font = pygame.font.Font('freesansbold.ttf', 30)
        self.mode = "neutral"

    def draw_game_state(self, game_state):
        for row in range(9):
            for col in range(9):
                pygame.draw.rect(self.display_surface, FG_COLOR, ((SQUARE_SIZE + WALL_THICKNESS) * col,
                                                                  (SQUARE_SIZE + WALL_THICKNESS) * row,
                                                                  SQUARE_SIZE, SQUARE_SIZE))
                if [col, row] == game_state.first_player_pos:
                    x_pos = (SQUARE_SIZE + WALL_THICKNESS) * col + SQUARE_SIZE / 2
                    y_pos = (SQUARE_SIZE + WALL_THICKNESS) * row + SQUARE_SIZE / 2
                    pygame.draw.circle(self.display_surface, FP_COLOR, (x_pos, y_pos), SQUARE_SIZE / 2)
                elif [col, row] == game_state.second_player_pos:
                    x_pos = (SQUARE_SIZE + WALL_THICKNESS) * col + SQUARE_SIZE / 2
                    y_pos = (SQUARE_SIZE + WALL_THICKNESS) * row + SQUARE_SIZE / 2
                    pygame.draw.circle(self.display_surface, SP_COLOR, (x_pos, y_pos), SQUARE_SIZE / 2)

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

        turn_text = "Red player" if game_state.first_player_turn else "Blue player"
        self.display_surface.blit(self.font.render(f"{turn_text}'s turn", True, FONT_COLOR),
                                  ((SQUARE_SIZE + WALL_THICKNESS) * 9, 0))
        self.display_surface.blit(
            self.font.render(f"Red player: {game_state.first_player_walls} walls", True, FONT_COLOR),
            ((SQUARE_SIZE + WALL_THICKNESS) * 9, 100))
        self.display_surface.blit(
            self.font.render(f"Blue player: {game_state.second_player_walls} walls", True, FONT_COLOR),
            ((SQUARE_SIZE + WALL_THICKNESS) * 9, 150))

        if game_state.winner == "first_player":
            winner_text = " Winner is: Red player"
        elif game_state.winner == "second_player":
            winner_text = "Winner is: Blue player"
        else:
            winner_text = ""
        self.display_surface.blit(
            self.font.render(winner_text, True, FONT_COLOR),
            ((SQUARE_SIZE + WALL_THICKNESS) * 9, 200))
        pygame.draw.rect(self.display_surface, FG_COLOR, ((SQUARE_SIZE + WALL_THICKNESS) * 9, 300, 300, 50))
        self.display_surface.blit(self.font.render("Place horizontal wall", True, FONT_COLOR),
                                  ((SQUARE_SIZE + WALL_THICKNESS) * 9, 312))
        pygame.draw.rect(self.display_surface, FG_COLOR, ((SQUARE_SIZE + WALL_THICKNESS) * 9, 400, 300, 50))
        self.display_surface.blit(self.font.render("Place vertical wall", True, FONT_COLOR),
                                  ((SQUARE_SIZE + WALL_THICKNESS) * 9, 412))
        if self.mode == "vertical_wall":
            x_position, y_position = pygame.mouse.get_pos()
            x_position = x_position // (SQUARE_SIZE + WALL_THICKNESS)
            x_position = 7 if x_position > 7 else x_position
            x_position = x_position * (SQUARE_SIZE + WALL_THICKNESS) + SQUARE_SIZE
            y_position = y_position // (SQUARE_SIZE + WALL_THICKNESS)
            y_position = 7 if y_position > 7 else y_position
            y_position *= (SQUARE_SIZE + WALL_THICKNESS)
            pygame.draw.rect(self.display_surface, WALL_HIGHLIGHT,
                             (x_position, y_position, WALL_THICKNESS, 2 * SQUARE_SIZE + WALL_THICKNESS))
        elif self.mode == "horizontal_wall":
            x_position, y_position = pygame.mouse.get_pos()
            x_position = x_position // (SQUARE_SIZE + WALL_THICKNESS)
            x_position = 7 if x_position > 7 else x_position
            x_position *= (SQUARE_SIZE + WALL_THICKNESS)
            y_position = y_position // (SQUARE_SIZE + WALL_THICKNESS)
            y_position = 7 if y_position > 7 else y_position
            y_position = y_position * (SQUARE_SIZE + WALL_THICKNESS) + SQUARE_SIZE
            pygame.draw.rect(self.display_surface, WALL_HIGHLIGHT,
                             (x_position, y_position, 2 * SQUARE_SIZE + WALL_THICKNESS, WALL_THICKNESS))

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    x_coord = event.pos[0] // (SQUARE_SIZE + WALL_THICKNESS)
                    y_coord = event.pos[1] // (SQUARE_SIZE + WALL_THICKNESS)
                    if x_coord < 9 and y_coord < 9 and self.mode == "neutral":
                        self.gs.move([x_coord, y_coord])
                    elif 9 <= x_coord < 14 and y_coord == 5:
                        if self.mode == "horizontal_wall":
                            self.mode = "neutral"
                        elif (self.gs.first_player_turn and self.gs.first_player_walls > 0) or (
                                (not self.gs.first_player_turn) and self.gs.second_player_walls > 0):
                            self.mode = "horizontal_wall"
                    elif 9 <= x_coord < 14 and y_coord == 7:
                        if self.mode == "vertical_wall":
                            self.mode = "neutral"
                        elif (self.gs.first_player_turn and self.gs.first_player_walls > 0) or (
                                (not self.gs.first_player_turn) and self.gs.second_player_walls > 0):
                            self.mode = "vertical_wall"
                    elif self.mode in ["horizontal_wall", "vertical_wall"]:
                        x_coord = 7 if x_coord > 7 else x_coord
                        y_coord = 7 if y_coord > 7 else y_coord
                        self.gs.place_wall((x_coord, y_coord), self.mode)
                        self.mode = "neutral"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_u:
                        self.gs.undo()
                        self.mode = "neutral"
                    elif event.key == pygame.K_r:
                        self.gs.redo()
                        self.mode = "neutral"
                    elif event.key == pygame.K_q:
                        self.gs.__init__()
                        self.mode = "neutral"

            # draw
            self.display_surface.fill(BG_COLOR)
            self.draw_game_state(self.gs)
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
