import pygame
import random

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Configuración de la pantalla
WIDTH = 400
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pou Jump")

# Colores
BLUE = (135, 206, 235)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# Cargar la imagen del jugador
player_img = pygame.image.load('game_corazon/cuerpo.png').convert_alpha()
player_img = pygame.transform.scale(player_img, (45, 45))
player_rect = player_img.get_rect()
player_rect.centerx = WIDTH // 2
player_rect.bottom = HEIGHT - 10

# Parámetros del jugador
player_speed = 5
player_jump = -15
player_y_momentum = 0

# Plataformas
platform_width = 60
platform_height = 10

# Tipos de plataformas
NORMAL = 0
MOVING = 1
FRAGILE = 2

# Sonidos
jump_sound = pygame.mixer.Sound('jump.wav')  # Asegúrate de tener este archivo
coin_sound = pygame.mixer.Sound('coin.wav')  # Asegúrate de tener este archivo

# Música de fondo
pygame.mixer.music.load('background_music.mp3')  # Asegúrate de tener este archivo
pygame.mixer.music.play(-1)  # El -1 hace que la música se repita indefinidamente

# Power-ups
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill(YELLOW)
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

# Puntuación
score = 0
font = pygame.font.Font(None, 36)

# Función para mostrar la pantalla de Game Over
def show_game_over():
    screen.fill(BLUE)
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Puntuación final: {score}", True, (0, 0, 0))
    restart_text = font.render("Presiona R para reiniciar", True, (0, 0, 0))
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
    screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 50))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True
    return False

# Bucle principal del juego
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Movimiento del jugador
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_rect.left > 0:
        player_rect.x -= player_speed
    if keys[pygame.K_RIGHT] and player_rect.right < WIDTH:
        player_rect.x += player_speed
    
    # Aplicar gravedad
    player_y_momentum += 0.5
    player_rect.y += player_y_momentum
    
    # Colisión con plataformas
    for platform, platform_type in platforms:
        if player_rect.colliderect(platform) and player_y_momentum > 0:
            if platform_type == FRAGILE:
                platforms.remove((platform, platform_type))
            else:
                player_rect.bottom = platform.top
                player_y_momentum = player_jump
                jump_sound.play()

    # Movimiento lateral continuo (efecto envolvente)
    if player_rect.left > WIDTH:
        player_rect.right = 0
    elif player_rect.right < 0:
        player_rect.left = WIDTH
    
    # Mover la pantalla hacia abajo cuando el jugador sube
    if player_rect.top <= HEIGHT // 2:
        player_rect.y += 5
        for platform, _ in platforms:
            platform.y += 5
        for power_up in power_ups:
            power_up.rect.y += 5
        
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
    power_up_collisions = pygame.sprite.spritecollide(player_rect, power_ups, True)
    for _ in power_up_collisions:
        score += 50
        coin_sound.play()
    
    # Perder si el jugador cae
    if player_rect.top > HEIGHT:
        if show_game_over():
            # Reiniciar el juego
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
        else:
            running = False
    
    # Dibujar todo
    screen.fill(BLUE)
    screen.blit(player_img, player_rect)
    for platform, platform_type in platforms:
        if platform_type == NORMAL:
            pygame.draw.rect(screen, GREEN, platform)
        elif platform_type == MOVING:
            pygame.draw.rect(screen, YELLOW, platform)
        elif platform_type == FRAGILE:
            pygame.draw.rect(screen, RED, platform)
    power_ups.draw(screen)
    
    # Mostrar puntuación
    score_text = font.render(f"Puntuación: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()