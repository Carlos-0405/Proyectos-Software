# Importación de bibliotecas necesarias
import pygame  # Para la interfaz gráfica
import numpy as np  # Para operaciones matemáticas y matrices
import pickle  # Para guardar/cargar el modelo entrenado
import sys  # Para funciones del sistema
from pygame import gfxdraw  # Para gráficos adicionales

# Inicialización de Pygame y su sistema de sonido
pygame.init()
pygame.mixer.init()

# Definición de constantes del juego
WINDOW_SIZE = 800  # Tamaño total de la ventana (incluye panel lateral)
BOARD_SIZE = 600   # Tamaño del tablero de juego
CELL_SIZE = BOARD_SIZE // 3  # Tamaño de cada celda del tablero
LINE_WIDTH = 15  # Grosor de las líneas del tablero
WINNING_LINE_WIDTH = 15  # Grosor de la línea que marca la victoria
PIECE_SIZE = 150  # Tamaño de las fichas X/O en el tablero
SIDE_PIECE_SIZE = 80  # Tamaño de las fichas en el panel lateral

# Carga y preparación de imágenes
try:
    # Cargar imágenes originales
    X_IMG = pygame.image.load('gato_game/x.png')
    O_IMG = pygame.image.load('gato_game/o.png')
    # Escalar imágenes para el tablero principal
    X_IMG_SCALED = pygame.transform.scale(X_IMG, (PIECE_SIZE, PIECE_SIZE))
    O_IMG_SCALED = pygame.transform.scale(O_IMG, (PIECE_SIZE, PIECE_SIZE))
    # Escalar imágenes para el panel lateral
    X_IMG_SIDE = pygame.transform.scale(X_IMG, (SIDE_PIECE_SIZE, SIDE_PIECE_SIZE))
    O_IMG_SIDE = pygame.transform.scale(O_IMG, (SIDE_PIECE_SIZE, SIDE_PIECE_SIZE))
except:
    print("Error al cargar las imágenes x.png y o.png")
    sys.exit(1)

# Carga del sonido para victoria
try:
    WINNER_SOUND = pygame.mixer.Sound('gato_game/Siuu.mp3')
except:
    print("No se pudo cargar el archivo de sonido")

# Definición de colores usando RGB
BG_COLOR = (40, 40, 80)          # Azul oscuro para el fondo
LINE_COLOR = (60, 60, 100)       # Azul más claro para las líneas
WINNING_LINE_COLOR = (255, 0, 255)  # Magenta neón para la línea ganadora
TEXT_COLOR = (255, 255, 255)     # Blanco para el texto

# Configuración de la ventana del juego
screen = pygame.display.set_mode((WINDOW_SIZE, BOARD_SIZE))
pygame.display.set_caption('Tres en Raya con IA Avanzada')

# Configuración de las fuentes para el texto
try:
    font = pygame.font.Font(None, 74)  # Fuente grande para mensajes de victoria
    side_font = pygame.font.Font(None, 36)  # Fuente pequeña para panel lateral
except:
    print("Error al cargar la fuente")

class NeuralNetwork:
    """
    Implementación de una red neuronal para la IA del juego
    Arquitectura: 16 neuronas entrada -> 64 neuronas ocultas -> 9 neuronas salida
    """
    def __init__(self, input_size=16, hidden_size=64, output_size=9):
        # Inicialización de pesos con valores aleatorios pequeños
        self.weights1 = np.random.randn(input_size, hidden_size) * 0.1
        self.weights2 = np.random.randn(hidden_size, output_size) * 0.1
        self.learning_rate = 0.20  # Tasa de aprendizaje
        
    def sigmoid(self, x):
        """Función de activación sigmoid para la capa de salida"""
        return 1 / (1 + np.exp(-x))
    
    def sigmoid_derivative(self, x):
        """Derivada de la función sigmoid para backpropagation"""
        return x * (1 - x)
    
    def relu(self, x):
        """Función de activación ReLU para la capa oculta"""
        return np.maximum(0, x)
    
    def relu_derivative(self, x):
        """Derivada de ReLU para backpropagation"""
        return np.where(x > 0, 1, 0)
    
    def forward(self, X):
        """Propagación hacia adelante en la red"""
        self.hidden = self.relu(np.dot(X, self.weights1))
        self.output = self.sigmoid(np.dot(self.hidden, self.weights2))
        return self.output
    
    def backward(self, X, y, output):
        """
        Retropropagación del error para ajustar los pesos
        Usa momentum para mejorar el aprendizaje
        """
        self.output_error = y - output
        self.output_delta = self.output_error * self.sigmoid_derivative(output)
        
        self.hidden_error = np.dot(self.output_delta, self.weights2.T)
        self.hidden_delta = self.hidden_error * self.relu_derivative(self.hidden)
        
        # Actualización de pesos con momentum
        self.weights1 += self.learning_rate * np.outer(X, self.hidden_delta)
        self.weights2 += self.learning_rate * np.outer(self.hidden, self.output_delta)

class TicTacToe:
    """
    Clase principal que maneja la lógica del juego
    Incluye la IA y el estado del tablero
    """
    def __init__(self):
        self.board = [' ' for _ in range(9)]  # Tablero vacío
        self.neural_net = NeuralNetwork()  # Inicializar red neuronal
        self.game_history = []  # Historial para entrenamiento
        self.load_neural_net()  # Cargar red neuronal pre-entrenada
        self.winner = None
        self.game_over = False
        self.winning_line = None
        # Definir todas las combinaciones ganadoras posibles
        self.winning_combinations = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Filas
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columnas
            [0, 4, 8], [2, 4, 6]  # Diagonales
        ]
        
    def load_neural_net(self):
        """Cargar red neuronal pre-entrenada desde archivo"""
        try:
            with open('tictactoe_ai_hard.pkl', 'rb') as f:
                self.neural_net = pickle.load(f)
        except:
            print("Creando nueva red neuronal")
    
    def save_neural_net(self):
        """Guardar red neuronal entrenada en archivo"""
        with open('tictactoe_ai_hard.pkl', 'wb') as f:
            pickle.dump(self.neural_net, f)
    
    def evaluate_position(self, board_state, player):
        """
        Evalúa la posición actual del tablero para un jugador
        Retorna un puntaje basado en la situación táctica
        """
        score = 0
        opponent = 'X' if player == 'O' else 'O'
        
        # Analizar cada combinación ganadora
        for combo in self.winning_combinations:
            line = [board_state[i] for i in combo]
            
            # Victoria inmediata: máxima prioridad
            if line.count(player) == 2 and line.count(' ') == 1:
                score += 1000
            
            # Bloqueo necesario: segunda prioridad
            elif line.count(opponent) == 2 and line.count(' ') == 1:
                score += 900
            
            # Crear amenaza doble
            elif line.count(player) == 1 and line.count(' ') == 2:
                score += 50
            
            # Prevenir amenazas del oponente
            elif line.count(opponent) == 1 and line.count(' ') == 2:
                score += 30
        
        # Valorar posiciones estratégicas
        strategic_positions = {
            4: 25,    # Centro
            0: 15,    # Esquinas
            2: 15,
            6: 15,
            8: 15,
            1: 5,     # Bordes
            3: 5,
            5: 5,
            7: 5
        }
        
        # Sumar valor de posiciones ocupadas
        for pos, value in strategic_positions.items():
            if board_state[pos] == player:
                score += value
                
        return score

    def make_move(self, position, player):
        """Realizar un movimiento en el tablero"""
        if self.board[position] == ' ' and not self.game_over:
            self.board[position] = player
            if self.check_winner():
                self.game_over = True
            return True
        return False
    
    def get_board_state(self):
        """Convertir estado del tablero a formato para la red neuronal"""
        state = []
        for cell in self.board:
            if cell == 'X':
                state.append(1)
            elif cell == 'O':
                state.append(-1)
            else:
                state.append(0)
        return np.array(state)
    
    def get_valid_moves(self):
        """Obtener lista de movimientos válidos"""
        return [i for i, cell in enumerate(self.board) if cell == ' ']
    
    def check_winner(self):
        """Verificar si hay un ganador o empate"""
        for combo in self.winning_combinations:
            if (self.board[combo[0]] != ' ' and
                self.board[combo[0]] == self.board[combo[1]] == self.board[combo[2]]):
                self.winner = self.board[combo[0]]
                self.winning_line = combo
                return True
        
        if ' ' not in self.board:
            self.winner = 'Empate'
            return True
        
        return False
    
    def ai_move(self):
        """
        Determinar el mejor movimiento para la IA
        Combina predicciones de la red neuronal con evaluación posicional
        """
        if self.game_over:
            return None
            
        board_state = self.get_board_state()
        predictions = self.neural_net.forward(board_state)
        valid_moves = self.get_valid_moves()
        
        # Buscar victoria inmediata
        for move in valid_moves:
            temp_board = self.board.copy()
            temp_board[move] = 'O'
            for combo in self.winning_combinations:
                if (temp_board[combo[0]] == temp_board[combo[1]] == temp_board[combo[2]] == 'O'):
                    return move
        
        # Bloquear victoria del oponente
        for move in valid_moves:
            temp_board = self.board.copy()
            temp_board[move] = 'X'
            for combo in self.winning_combinations:
                if (temp_board[combo[0]] == temp_board[combo[1]] == temp_board[combo[2]] == 'X'):
                    return move
        
        # Evaluar mejor movimiento combinando estrategia y red neuronal
        move_scores = {}
        for move in valid_moves:
            temp_board = self.board.copy()
            temp_board[move] = 'O'
            
            strategic_score = self.evaluate_position(temp_board, 'O')
            neural_score = predictions[move]
            
            # 70% estrategia, 30% red neuronal
            combined_score = 0.7 * strategic_score + 0.3 * neural_score * 100
            move_scores[move] = combined_score
        
        if not move_scores:
            return None
        
        best_move = max(move_scores.items(), key=lambda x: x[1])[0]
        return best_move
    
    def train_ai(self):
        """Entrenar la red neuronal con el historial de la partida"""
        reward_multiplier = 2.0
        
        for state, move in self.game_history:
            target = np.zeros(9)
            if self.winner == 'O':
                target[move] = 1 * reward_multiplier  # Refuerzo positivo
            elif self.winner == 'X':
                target[move] = -1 * reward_multiplier  # Refuerzo negativo
            else:
                target[move] = 0.5  # Empate
            
            output = self.neural_net.forward(state)
            self.neural_net.backward(state, target, output)

# Funciones de la interfaz gráfica
def draw_side_panel():
    """Dibujar panel lateral con información"""
    pygame.draw.rect(screen, (30, 30, 60), (BOARD_SIZE, 0, WINDOW_SIZE - BOARD_SIZE, BOARD_SIZE))
    title = side_font.render("FICHAS", True, TEXT_COLOR)
    screen.blit(title, (BOARD_SIZE + 50, 50))
    screen.blit(X_IMG_SIDE, (BOARD_SIZE + 60, 120))
    screen.blit(O_IMG_SIDE, (BOARD_SIZE + 60, 250))

def draw_winner_message(winner):
    """Mostrar mensaje de ganador o empate"""
    if winner == 'Empate':
        text = '¡EMPATE!'
    else:
        text = f'¡GANADOR {winner}!'
    
    # Crear fondo semitransparente
    s = pygame.Surface((BOARD_SIZE, 100))
    s.set_alpha(128)
    s.fill((0, 0, 0))
    screen.blit(s, (0, BOARD_SIZE//2 - 50))
    
    # Mostrar mensaje
    text_surface = font.render(text, True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(BOARD_SIZE//2, BOARD_SIZE//2))
    screen.blit(text_surface, text_rect)
    
    # Reproducir sonido de victoria
    try:
        WINNER_SOUND.play()
    except:
        pass
def draw_lines():
    """Dibujar líneas del tablero"""
    # Líneas verticales
    pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE, 0), (CELL_SIZE, BOARD_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (CELL_SIZE * 2, 0), (CELL_SIZE * 2, BOARD_SIZE), LINE_WIDTH)
    # Líneas horizontales
    pygame.draw.line(screen, LINE_COLOR, (0, CELL_SIZE), (BOARD_SIZE, CELL_SIZE), LINE_WIDTH)
    pygame.draw.line(screen, LINE_COLOR, (0, CELL_SIZE * 2), (BOARD_SIZE, CELL_SIZE * 2), LINE_WIDTH)

def draw_winning_line(winning_combination):
    """
    Dibujar la línea que marca la combinación ganadora
    winning_combination: lista de 3 índices que forman la línea ganadora
    """
    if winning_combination is None:
        return
    
    # Calcular posiciones de inicio y fin de la línea
    start_pos = (
        (winning_combination[0] % 3) * CELL_SIZE + CELL_SIZE // 2,  # x inicial
        (winning_combination[0] // 3) * CELL_SIZE + CELL_SIZE // 2   # y inicial
    )
    end_pos = (
        (winning_combination[2] % 3) * CELL_SIZE + CELL_SIZE // 2,   # x final
        (winning_combination[2] // 3) * CELL_SIZE + CELL_SIZE // 2    # y final
    )
    
    # Dibujar línea en color magenta neón
    pygame.draw.line(screen, WINNING_LINE_COLOR, start_pos, end_pos, WINNING_LINE_WIDTH)

def draw_figures(board):
    """
    Dibujar las X y O en el tablero
    board: lista que representa el estado actual del tablero
    """
    for row in range(3):
        for col in range(3):
            # Calcular el centro de cada celda
            cell_center_x = col * CELL_SIZE + (CELL_SIZE - PIECE_SIZE) // 2
            cell_center_y = row * CELL_SIZE + (CELL_SIZE - PIECE_SIZE) // 2
            
            # Dibujar X u O según corresponda
            if board[row * 3 + col] == 'X':
                screen.blit(X_IMG_SCALED, (cell_center_x, cell_center_y))
            elif board[row * 3 + col] == 'O':
                screen.blit(O_IMG_SCALED, (cell_center_x, cell_center_y))

def get_square_from_mouse(pos):
    """
    Convertir la posición del mouse a índice del tablero
    pos: tupla (x, y) con la posición del mouse
    Retorna: índice de la casilla o None si está fuera del tablero
    """
    x, y = pos
    if x >= BOARD_SIZE:  # Si el clic está en el panel lateral
        return None
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    return row * 3 + col

def main():
    """Función principal del juego"""
    # Inicializar el juego
    game = TicTacToe()
    screen.fill(BG_COLOR)
    draw_lines()
    draw_side_panel()

    # Bucle principal del juego
    while True:
        # Procesar eventos
        for event in pygame.event.get():
            # Evento de cierre de ventana
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # Evento de clic del mouse
            if event.type == pygame.MOUSEBUTTONDOWN and not game.game_over:
                pos = pygame.mouse.get_pos()
                square = get_square_from_mouse(pos)
                
                # Procesar movimiento del jugador
                if square is not None and game.make_move(square, 'X'):
                    # Actualizar pantalla después del movimiento del jugador
                    screen.fill(BG_COLOR)
                    draw_lines()
                    draw_figures(game.board)
                    draw_side_panel()
                    
                    # Verificar si hay ganador
                    if game.winning_line:
                        draw_winning_line(game.winning_line)
                        draw_winner_message(game.winner)
                    pygame.display.update()
                    
                    # Si el juego terminó, entrenar la IA y guardar
                    if game.game_over:
                        game.train_ai()
                        game.save_neural_net()
                        continue
                    
                    # Turno de la IA
                    ai_move = game.ai_move()
                    if ai_move is not None:
                        # Realizar movimiento de la IA
                        game.make_move(ai_move, 'O')
                        game.game_history.append((game.get_board_state(), ai_move))
                        
                        # Actualizar pantalla después del movimiento de la IA
                        screen.fill(BG_COLOR)
                        draw_lines()
                        draw_figures(game.board)
                        draw_side_panel()
                        
                        # Verificar si hay ganador
                        if game.winning_line:
                            draw_winning_line(game.winning_line)
                            draw_winner_message(game.winner)
                        
                        # Si el juego terminó, entrenar la IA y guardar
                        if game.game_over:
                            game.train_ai()
                            game.save_neural_net()
            
            # Evento de tecla presionada
            if event.type == pygame.KEYDOWN:
                # Reiniciar juego con tecla 'R'
                if event.key == pygame.K_r:
                    game = TicTacToe()
                    screen.fill(BG_COLOR)
                    draw_lines()
                    draw_side_panel()
        
        # Actualizar la pantalla
        pygame.display.update()

# Punto de entrada del programa
if __name__ == "__main__":
    main()