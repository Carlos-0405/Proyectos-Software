import pygame
import numpy as np
import random
import pickle
import sys
from pygame.locals import *

# Configuración básica
pygame.init()
BOARD_SIZE = 5
CELL_SIZE = 100
SCREEN_SIZE = BOARD_SIZE * CELL_SIZE
FPS = 30
LINE_WIDTH = 5
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Pantalla
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Tic Tac Toe AI")

# Cargar recursos
try:
    x_img = pygame.image.load("gato_game/x.png")
    o_img = pygame.image.load("gato_game/o.png")
    x_img = pygame.transform.scale(x_img, (CELL_SIZE, CELL_SIZE))
    o_img = pygame.transform.scale(o_img, (CELL_SIZE, CELL_SIZE))
except pygame.error:
    print("Error al cargar las imágenes. Verifica los archivos.")
    sys.exit(1)

try:
    win_sound = pygame.mixer.Sound("gato_game/Siuu.mp3")
except pygame.error:
    print("Error al cargar el sonido. Continuando sin sonido.")
    win_sound = None

# Modelo IA
class TicTacToeAI:
    def __init__(self):
        self.q_table = {}

    def save(self, filename="tictactoe_ai_hard.pkl"):
        with open(filename, "wb") as f:
            pickle.dump(self.q_table, f)

    def load(self, filename="tictactoe_ai_hard.pkl"):
        try:
            with open(filename, "rb") as f:
                self.q_table = pickle.load(f)
        except FileNotFoundError:
            print("Archivo de IA no encontrado. Creando nuevo modelo.")

    def choose_action(self, state, valid_actions, epsilon=0.1):
        if random.random() < epsilon:
            return random.choice(valid_actions)
        q_values = [self.q_table.get((state, action), 0) for action in valid_actions]
        max_q = max(q_values)
        return valid_actions[q_values.index(max_q)]

    def update_q_value(self, state, action, reward, next_state, alpha=0.1, gamma=0.9):
        old_value = self.q_table.get((state, action), 0)
        future_value = max([self.q_table.get((next_state, a), 0) for a in range(BOARD_SIZE ** 2)], default=0)
        self.q_table[(state, action)] = old_value + alpha * (reward + gamma * future_value - old_value)

# Tablero
class Board:
    def __init__(self):
        self.grid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.winner = None

    def mark_cell(self, row, col, player):
        if self.grid[row, col] == 0:
            self.grid[row, col] = player
            return True
        return False

    def check_winner(self):
        for row in range(BOARD_SIZE):
            if abs(sum(self.grid[row, :])) == BOARD_SIZE:
                self.winner = np.sign(sum(self.grid[row, :]))
                return True
        for col in range(BOARD_SIZE):
            if abs(sum(self.grid[:, col])) == BOARD_SIZE:
                self.winner = np.sign(sum(self.grid[:, col]))
                return True
        if abs(sum(self.grid.diagonal())) == BOARD_SIZE or abs(sum(np.fliplr(self.grid).diagonal())) == BOARD_SIZE:
            self.winner = np.sign(sum(self.grid.diagonal())) if abs(sum(self.grid.diagonal())) == BOARD_SIZE else np.sign(sum(np.fliplr(self.grid).diagonal()))
            return True
        if not any(0 in row for row in self.grid):
            self.winner = 0  # Empate
            return True
        return False

    def reset(self):
        self.grid = np.zeros((BOARD_SIZE, BOARD_SIZE), dtype=int)
        self.winner = None

# Dibujar en pantalla
def draw_lines():
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(screen, BLACK, (0, i * CELL_SIZE), (SCREEN_SIZE, i * CELL_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, SCREEN_SIZE), LINE_WIDTH)

def draw_figures(board):
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if board.grid[row, col] == 1:
                screen.blit(x_img, (col * CELL_SIZE, row * CELL_SIZE))
            elif board.grid[row, col] == -1:
                screen.blit(o_img, (col * CELL_SIZE, row * CELL_SIZE))

def draw_winner_message(winner):
    font = pygame.font.Font(None, 74)
    if winner == 1:
        text = font.render("Jugador X Gana!", True, RED)
    elif winner == -1:
        text = font.render("Jugador O Gana!", True, BLUE)
    else:
        text = font.render("Empate!", True, BLACK)
    screen.fill(WHITE)
    screen.blit(text, (SCREEN_SIZE // 4, SCREEN_SIZE // 2 - 50))
    if win_sound:
        win_sound.play()
    pygame.display.update()
    pygame.time.wait(3000)

# Main Loop
def main():
    clock = pygame.time.Clock()
    board = Board()
    ai = TicTacToeAI()
    ai.load()

    running = True
    player_turn = 1

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            if event.type == KEYDOWN and event.key == K_r:
                board.reset()
                player_turn = 1
            if event.type == MOUSEBUTTONDOWN and player_turn == 1 and board.winner is None:
                mouseX, mouseY = pygame.mouse.get_pos()
                clicked_row = mouseY // CELL_SIZE
                clicked_col = mouseX // CELL_SIZE
                if board.mark_cell(clicked_row, clicked_col, player_turn):
                    player_turn = -1

        if player_turn == -1 and board.winner is None:
            state = tuple(map(tuple, board.grid))
            valid_actions = [i for i in range(BOARD_SIZE ** 2) if board.grid[i // BOARD_SIZE, i % BOARD_SIZE] == 0]
            action = ai.choose_action(state, valid_actions)
            board.mark_cell(action // BOARD_SIZE, action % BOARD_SIZE, player_turn)
            player_turn = 1

        screen.fill(WHITE)
        draw_lines()
        draw_figures(board)
        pygame.display.update()

        if board.check_winner():
            draw_winner_message(board.winner)
            board.reset()

        clock.tick(FPS)

    ai.save()
    pygame.quit()

if __name__ == "__main__":
    main()
