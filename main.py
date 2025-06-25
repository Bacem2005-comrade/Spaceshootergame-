import pygame
import sys
import random
import math
from pygame import mixer

# Initialize PyGame
pygame.init()

# Set up the game window
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Attack")

# Set the frame rate
clock = pygame.time.Clock()

# Load images with error handling
try:
    # Background
    background = pygame.image.load('bg.jpg')
    background = pygame.transform.scale(background, (screen_width, screen_height))
except:
    print("Could not load background image. Using black background.")
    background = None

try:
    # Player
    player_img = pygame.image.load('player_spaceship.png')
    player_img = pygame.transform.scale(player_img, (50, 60))
except:
    print("Could not load player image. Using rectangle instead.")
    player_img = None

try:
    # Enemy
    enemy_img = pygame.image.load('alien.png')
    enemy_img = pygame.transform.scale(enemy_img, (50, 60))
except:
    print("Could not load enemy image. Using rectangle instead.")
    enemy_img = None

try:
    # Bullet - made larger for better visibility
    bullet_img = pygame.image.load('bullet.png')
    bullet_img = pygame.transform.scale(bullet_img, (10, 20))  # Increased size
except:
    print("Could not load bullet image. Using rectangle instead.")
    bullet_img = None

# Load sounds
try:
    mixer.music.load('background.wav')
    mixer.music.set_volume(0.5)
    mixer.music.play(-1)
except:
    print("Could not load background music.")

try:
    laser_sound = mixer.Sound('laser.wav')
    explosion_sound = mixer.Sound('explosion.wav')
except:
    print("Could not load sound effects.")
    laser_sound = None
    explosion_sound = None

# Game state
def init_game():
    global player_x, player_y, bullets, enemies, score, game_over, enemy_timer
    
    # Player settings
    player_x = screen_width // 2 - player_width // 2
    player_y = screen_height - player_height - 10
    
    # Bullet settings
    bullets = []
    
    # Enemy settings
    enemies = []
    enemy_timer = pygame.time.get_ticks()
    
    # Score
    score = 0
    
    # Game over flag
    game_over = False

# Initialize game for the first time
player_width = 50
player_height = 60
player_speed = 5
bullet_width = 10  # Increased size
bullet_height = 20  # Increased size
bullet_speed = 10
enemy_width = 50
enemy_height = 60
enemy_speed = 2
enemy_spawn_time = 1000  # 1 second

init_game()

# Fonts
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
restart_font = pygame.font.Font(None, 48)

def draw_player(x, y):
    if player_img:
        screen.blit(player_img, (x, y))
    else:
        pygame.draw.rect(screen, (0, 128, 255), (x, y, player_width, player_height))

def draw_enemy(x, y):
    if enemy_img:
        screen.blit(enemy_img, (x, y))
    else:
        pygame.draw.rect(screen, (255, 0, 0), (x, y, enemy_width, enemy_height))

def draw_bullet(x, y):
    if bullet_img:
        screen.blit(bullet_img, (x, y))
    else:
        pygame.draw.rect(screen, (255, 255, 0), (x, y, bullet_width, bullet_height))  # Yellow for visibility

def show_score():
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

def show_game_over():
    game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
    screen.blit(game_over_text, (screen_width//2 - 150, screen_height//2 - 50))
    
    restart_text = restart_font.render("Press R to restart", True, (255, 255, 255))
    screen.blit(restart_text, (screen_width//2 - 120, screen_height//2 + 20))

def check_collision(bullet_x, bullet_y, enemy_x, enemy_y):
    # Using rectangular collision for better accuracy with the larger bullet
    bullet_rect = pygame.Rect(bullet_x, bullet_y, bullet_width, bullet_height)
    enemy_rect = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
    return bullet_rect.colliderect(enemy_rect)

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_SPACE and not game_over:
                # Fire bullet from center of player
                bullet_x = player_x + player_width // 2 - bullet_width // 2
                bullet_y = player_y
                bullets.append([bullet_x, bullet_y])
                if laser_sound:
                    laser_sound.play()
            if event.key == pygame.K_r and game_over:
                init_game()  # Reset game when R is pressed

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < screen_width - player_width:
            player_x += player_speed

        # Spawn enemies
        current_time = pygame.time.get_ticks()
        if current_time - enemy_timer > enemy_spawn_time:
            enemy_x = random.randint(0, screen_width - enemy_width)
            enemy_y = -enemy_height
            enemies.append([enemy_x, enemy_y, random.choice([-1, 1]) * enemy_speed])
            enemy_timer = current_time

        # Update bullets
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)

        # Update enemies and check collisions
        for enemy in enemies[:]:
            enemy[1] += enemy_speed
            
            # Check if enemy reached bottom
            if enemy[1] > screen_height - 50:
                game_over = True
            
            # Check for bullet collisions
            for bullet in bullets[:]:
                if check_collision(bullet[0], bullet[1], enemy[0], enemy[1]):
                    if explosion_sound:
                        explosion_sound.play()
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 1
                    break

    # Draw everything
    if background:
        screen.blit(background, (0, 0))
    else:
        screen.fill((0, 0, 0))

    for bullet in bullets:
        draw_bullet(bullet[0], bullet[1])

    for enemy in enemies:
        draw_enemy(enemy[0], enemy[1])

    draw_player(player_x, player_y)
    show_score()
    
    if game_over:
        show_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()


