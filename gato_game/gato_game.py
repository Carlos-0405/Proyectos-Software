import pygame
import numpy as np
import pickle
import sys

# Inicializar Pygame
pygame.init()

# Constantes
WINDOW_SIZE = 600
BOARD_SIZE = 500
CELL_SIZE = BOARD_SIZE // 5
LINE_WIDTH = 10
PIECE_SIZE = CELL_SIZE - 20

# Colores
BG_COLOR = (40, 40, 80)
LINE_COLOR = (60, 60, 100)
TEXT_COLOR = (255, 255, 255)
WINNING_LINE_COLOR = (255, 0, 255)

# Configuración de la ventana
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption('4 en Raya')

# Configuración de fuente
font = pygame.font.Font(None, 74)

class FourInARow:
    def __init__(self):
        self.board = [[" " for _ in range(5)] for _ in range(5)]
        self.current_player = "X"
        self.winner = None
        self.game_over = False

    def make_move(self, row, col):
        if self.board[row][col] == " " and not self.game_over:
            self.board[row][col] = self.current_player
            if self.check_winner(row, col):
                self.game_over = True
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
            return True
        return False

    def check_winner(self, row, col):
        directions = [
            [(0, 1), (0, -1)],  # Horizontal
            [(1, 0), (-1, 0)],  # Vertical
            [(1, 1), (-1, -1)],  # Diagonal \n            [(1, -1), (-1, 1)]  # Diagonal /
        ]
        
        for direction in directions:
            count = 1  # Incluir la ficha actual
            for dr, dc in direction:
                r, c = row, col
                while 0 <= r + dr < 5 and 0 <= c + dc < 5 and self.board[r + dr][c + dc] == self.current_player:
                    count += 1
                    r += dr
                    c += dc
                if count >= 4:
                    return True
        return False

    def is_full(self):
        return all(self.board[row][col] != " " for row in range(5) for col in range(5))

def draw_board(game):
    screen.fill(BG_COLOR)
    for row in range(6):
        pygame.draw.line(screen, LINE_COLOR, (0, row * CELL_SIZE), (BOARD_SIZE, row * CELL_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (row * CELL_SIZE, 0), (row * CELL_SIZE, BOARD_SIZE), LINE_WIDTH)

    for row in range(5):
        for col in range(5):
            if game.board[row][col] == "X":
                pygame.draw.line(
                    screen, TEXT_COLOR,
                    (col * CELL_SIZE + 10, row * CELL_SIZE + 10),
                    ((col + 1) * CELL_SIZE - 10, (row + 1) * CELL_SIZE - 10),
                    LINE_WIDTH
                )
                pygame.draw.line(
                    screen, TEXT_COLOR,
                    ((col + 1) * CELL_SIZE - 10, row * CELL_SIZE + 10),
                    (col * CELL_SIZE + 10, (row + 1) * CELL_SIZE - 10),
                    LINE_WIDTH
                )
            elif game.board[row][col] == "O":
                pygame.draw.circle(
                    screen, TEXT_COLOR,
                    (col * CELL_SIZE + CELL_SIZE // 2, row * CELL_SIZE + CELL_SIZE // 2),
                    PIECE_SIZE // 2,
                    LINE_WIDTH
                )

def draw_winner_message(winner):
    text = f'Ganador: {winner}' if winner else 'Empate'
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(WINDOW_SIZE // 2, WINDOW_SIZE // 2))
    screen.blit(text_surface, text_rect)

def main():
    game = FourInARow()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                x, y = pygame.mouse.get_pos()
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                if game.make_move(row, col):
                    if game.game_over:
                        draw_board(game)
                        draw_winner_message(game.current_player)
                    elif game.is_full():
                        game.game_over = True
                        draw_winner_message(None)

        draw_board(game)
        pygame.display.update()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
