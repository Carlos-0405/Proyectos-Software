import pygame
import random

# Inicializar Pygame y el módulo de mixer
pygame.init()
pygame.mixer.init()

# Configuración de la pantalla
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Keylita Jump")

# Colores
GROUND_COLOR = (34, 139, 34)  # Verde oscuro
SKY_COLOR = (135, 206, 235)   # Azul cielo
SPACE_COLOR = (25, 25, 112)   # Azul medianoche
DEEP_SPACE_COLOR = (0, 0, 0)  # Negro
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
DIRT_BROWN = (139, 69, 19)    # Color para la tierra
GRASS_GREEN = (34, 139, 34)   # Color para el pasto

# Fuentes
font = pygame.font.Font(None, 36)

# Cargar la imagen del jugador
player_img = pygame.image.load('game_corazon/cuerpo.png').convert_alpha()
player_img = pygame.transform.scale(player_img, (47, 47))
player_rect = player_img.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.bottom = HEIGHT - 10

# Parámetros del jugador
player_speed = 3
player_jump = -16
player_y_momentum = 0

# Plataformas
platform_width = 60
platform_height = 10

# Tipos de plataformas
NORMAL, MOVING, FRAGILE = range(3)

# Power-ups
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load('game_corazon/pastelito.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (20, 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

power_ups = pygame.sprite.Group()

# Función para crear plataformas
def create_platform(x, y, type=NORMAL):
    platform = pygame.Rect(x, y, platform_width, platform_height)
    return (platform, type)

# Generar plataformas iniciales
platforms = [create_platform(WIDTH // 2 - platform_width // 2, HEIGHT - 50)]
for i in range(10):
    x = random.randint(0, WIDTH - platform_width)
    y = HEIGHT - (i + 1) * 60
    platform_type = random.choices([NORMAL, MOVING, FRAGILE], weights=[0.6, 0.3, 0.1])[0]
    platforms.append(create_platform(x, y, platform_type))

# Función para interpolar colores
def interpolate_color(color1, color2, factor):
    return tuple(int(color1[i] + (color2[i] - color1[i]) * factor) for i in range(3))

# Función para obtener el color de fondo basado en la altura
def get_background_color(height):
    if height < 1000:
        return interpolate_color(GROUND_COLOR, SKY_COLOR, height / 1000)
    elif height < 5000:
        return interpolate_color(SKY_COLOR, SPACE_COLOR, (height - 1000) / 4000)
    else:
        return interpolate_color(SPACE_COLOR, DEEP_SPACE_COLOR, min((height - 5000) / 5000, 1))

# Estrellas para el fondo espacial
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT)) for _ in range(100)]

# Clase para botones
class Button:
    def __init__(self, x, y, width, height, text, color, text_color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        text_surface = font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Crear botones
play_button = Button(WIDTH//2-50, HEIGHT//2, 100, 50, 'Jugar', GREEN, WHITE)
restart_button = Button(WIDTH//2-50, HEIGHT//2+60, 100, 50, 'Reiniciar', RED, WHITE)

# Variables para el seguimiento de la altura y el puntaje
total_height = 0
score = 0
background_color = GROUND_COLOR

# Estado del juego
game_state = "menu"

# Lista de canciones
songs = ['game_corazon/cancion1.mp3', 'game_corazon/cancion2.mp3', 'game_corazon/cancion3.mp3']
current_song = None

# Función para reproducir una canción aleatoria
def play_random_song():
    global current_song
    if current_song:
        pygame.mixer.music.stop()
    new_song = random.choice(songs)
    while new_song == current_song:
        new_song = random.choice(songs)
    current_song = new_song
    pygame.mixer.music.load(current_song)
    pygame.mixer.music.play(-1)  # -1 significa reproducir en bucle

# Función para reiniciar el juego
def reset_game():
    global player_rect, player_y_momentum, platforms, power_ups, score, total_height, background_color
    player_rect.centerx = WIDTH // 2
    player_rect.bottom = HEIGHT - 10
    player_y_momentum = 0
    platforms = [create_platform(WIDTH // 2 - platform_width // 2, HEIGHT - 50)]
    for i in range(10):
        x = random.randint(0, WIDTH - platform_width)
        y = HEIGHT - (i + 1) * 60
        platform_type = random.choices([NORMAL, MOVING, FRAGILE], weights=[0.6, 0.3, 0.1])[0]
        platforms.append(create_platform(x, y, platform_type))
    power_ups.empty()
    score = 0
    total_height = 0
    background_color = GROUND_COLOR
    play_random_song()  # Reproducir una nueva canción aleatoria

# Iniciar la primera canción cuando se inicia el juego
play_random_song()

# Bucle principal del juego
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "menu" and play_button.is_clicked(event.pos):
                game_state = "playing"
                reset_game()  # Esto también cambiará la canción
            elif game_state == "game_over" and restart_button.is_clicked(event.pos):
                reset_game()
                game_state = "playing"
    
    if game_state == "playing":
        # Movimiento del jugador con teclado
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_rect.left > 0:
            player_rect.x -= player_speed
        if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
            player_rect.x += player_speed
        
        # Movimiento del jugador con touch
        touch_pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:  # Si hay un toque en la pantalla
            if touch_pos[0] < WIDTH // 2:  # Toque en la mitad izquierda
                if player_rect.left > 0:
                    player_rect.x -= player_speed
            else:  # Toque en la mitad derecha
                if player_rect.right < WIDTH:
                    player_rect.x += player_speed
        
        # Aplicar gravedad
        player_y_momentum += 0.3
        player_rect.y += player_y_momentum
        
        # Colisión con plataformas
        for platform, platform_type in platforms:
            if player_rect.colliderect(platform) and player_y_momentum > 0:
                if platform_type == FRAGILE:
                    platforms.remove((platform, platform_type))
                else:
                    player_rect.bottom = platform.top
                    player_y_momentum = player_jump

        # Movimiento lateral continuo (efecto envolvente)
        if player_rect.left > WIDTH:
            player_rect.right = 0
        elif player_rect.right < 0:
            player_rect.left = WIDTH
        
        # Actualizar la altura total y el color de fondo
        if player_rect.top <= HEIGHT // 2:
            distance_moved = HEIGHT // 2 - player_rect.top
            total_height += distance_moved
            player_rect.y += distance_moved
            background_color = get_background_color(total_height)

            # Mover las plataformas y power-ups
            for platform, _ in platforms:
                platform.y += distance_moved
            for power_up in power_ups:
                power_up.rect.y += distance_moved
            
            # Mover las estrellas
            stars = [(x, (y + distance_moved) % HEIGHT) for x, y in stars]
            
            # Eliminar plataformas que salen de la pantalla y crear nuevas
            platforms = [(p, t) for p, t in platforms if p.top < HEIGHT]
            while len(platforms) < 10:
                x = random.randint(0, WIDTH - platform_width)
                y = random.randint(-50, -10)
                platform_type = random.choices([NORMAL, MOVING, FRAGILE], weights=[0.6, 0.3, 0.1])[0]
                platforms.append(create_platform(x, y, platform_type))
                
                # Posibilidad de generar un power-up
                if random.random() < 0.1:  # 10% de probabilidad
                    power_up = PowerUp(x + platform_width // 2, y - 30)
                    power_ups.add(power_up)
            
            score += 1
        
        # Mover plataformas móviles
        for platform, platform_type in platforms:
            if platform_type == MOVING:
                platform.x += random.choice([-2, 2])
                if platform.left < 0 or platform.right > WIDTH:
                    platform.x *= -1
        
        # Colisión con power-ups
        for power_up in list(power_ups):
            if player_rect.colliderect(power_up.rect):
                power_ups.remove(power_up)
                score += 50
        
        # Perder si el jugador cae
        if player_rect.top > HEIGHT:
            game_state = "game_over"
    
    # Dibujar el fondo
    screen.fill(background_color)

    # Dibujar estrellas si estamos en el espacio
    if total_height > 1000:
        for star in stars:
            pygame.draw.circle(screen, WHITE, star, 1)

    if game_state == "playing" or game_state == "game_over":
        # Dibujar plataformas y jugador
        for platform, platform_type in platforms:
            pygame.draw.rect(screen, DIRT_BROWN, platform)
            grass_rect = pygame.Rect(platform.left, platform.top, platform.width, 5)
            if platform_type == NORMAL:
                pygame.draw.rect(screen, GRASS_GREEN, grass_rect)
            elif platform_type == MOVING:
                pygame.draw.rect(screen, YELLOW, grass_rect)
            elif platform_type == FRAGILE:
                pygame.draw.rect(screen, RED, grass_rect)
        power_ups.draw(screen)
        screen.blit(player_img, player_rect)
        
        # Mostrar puntuación y altura
        score_text = font.render(f"Puntuación: {score}", True, WHITE)
        height_text = font.render(f"Altura: {int(total_height)}m", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(height_text, (10, 40))

    if game_state == "menu":
        title_text = font.render("Keylita Jump", True, WHITE)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
        play_button.draw(screen)
    elif game_state == "game_over":
        game_over_text = font.render("Game Over", True, RED)
        screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//4))
        restart_button.draw(screen)
    
    pygame.display.flip()
    clock.tick(60)

# Detener la música y cerrar Pygame
pygame.mixer.music.stop()
pygame.quit()