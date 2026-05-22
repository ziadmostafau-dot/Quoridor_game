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
        self.place_horizontal_walls = pygame.Rect((SQUARE_SIZE + WALL_THICKNESS) * 9, 350, 300, 50)
        self.place_vertical_walls = pygame.Rect((SQUARE_SIZE + WALL_THICKNESS) * 9, 450, 300, 50)

    def draw_game_state(self, game_state):
        for row in range(9):
            for col in range(9):
                pygame.draw.rect(self.display_surface, FG_COLOR, ((SQUARE_SIZE + WALL_THICKNESS) * col,
                                                                  (SQUARE_SIZE + WALL_THICKNESS) * row,
                                                                  SQUARE_SIZE, SQUARE_SIZE))
                if ([row, col] == game_state.first_player_pos):
                    x_pos = (SQUARE_SIZE + WALL_THICKNESS) * col + SQUARE_SIZE / 2
                    y_pos = (SQUARE_SIZE + WALL_THICKNESS) * row + SQUARE_SIZE / 2
                    pygame.draw.circle(self.display_surface, FP_COLOR, (x_pos, y_pos), SQUARE_SIZE / 2)
                elif ([row, col] == game_state.second_player_pos):
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
            ((SQUARE_SIZE + WALL_THICKNESS) * 9, 300))
        pygame.draw.rect(self.display_surface, FG_COLOR, self.place_horizontal_walls)
        self.display_surface.blit(self.font.render("Place horizontal wall", True, FONT_COLOR),
                                  ((SQUARE_SIZE + WALL_THICKNESS) * 9, 362))
        pygame.draw.rect(self.display_surface, FG_COLOR, self.place_vertical_walls)
        self.display_surface.blit(self.font.render("Place vertical wall", True, FONT_COLOR),
                                  ((SQUARE_SIZE + WALL_THICKNESS) * 9, 462))

    def run(self):
        while self.running:
            dt = self.clock.tick(FRAMERATE) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # draw
            self.display_surface.fill(BG_COLOR)
            self.draw_game_state(self.gs)
            pygame.display.update()

        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()
