import pygame
import sys
import random
import math
from pygame import mixer
from typing import List, Tuple, Optional

# Constants (PEP 8: UPPER_CASE)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 10
ENEMY_SPEED = 2
ENEMY_SPAWN_TIME = 1000  # ms

class GameObject:
    """Base class for all game objects (player, enemies, bullets)."""
    
    def __init__(self, x: int, y: int, width: int, height: int, image_path: Optional[str] = None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.image = self._load_image(image_path) if image_path else None

    def _load_image(self, path: str) -> Optional[pygame.Surface]:
        """Load and scale an image with error handling."""
        try:
            img = pygame.image.load(path)
            return pygame.transform.scale(img, (self.width, self.height))
        except Exception as e:
            print(f"Error loading image: {e}. Using placeholder.")
            return None

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the object (image or rectangle)."""
        if self.image:
            screen.blit(self.image, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def get_rect(self) -> pygame.Rect:
        """Return collision rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Player(GameObject):
    """Player spaceship controlled by arrow keys."""
    
    def __init__(self):
        super().__init__(
            x=SCREEN_WIDTH // 2 - 25,
            y=SCREEN_HEIGHT - 70,
            width=50,
            height=60,
            image_path="player_spaceship.png"
        )
        self.color = (0, 128, 255)  # Blue fallback
        self.speed = PLAYER_SPEED

    def update(self) -> None:
        """Move player based on keyboard input."""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed

class Enemy(GameObject):
    """Enemy spaceship that moves downward."""
    
    def __init__(self, x: int):
        super().__init__(
            x=x,
            y=-60,
            width=50,
            height=60,
            image_path="alien.png"
        )
        self.color = (255, 0, 0)  # Red fallback
        self.speed = ENEMY_SPEED

    def update(self) -> bool:
        """Move enemy. Returns True if it reached the bottom."""
        self.y += self.speed
        return self.y > SCREEN_HEIGHT

class Bullet(GameObject):
    """Bullet fired by the player."""
    
    def __init__(self, x: int, y: int):
        super().__init__(
            x=x,
            y=y,
            width=10,
            height=20,
            image_path="bullet.png"
        )
        self.color = (255, 255, 0)  # Yellow fallback
        self.speed = BULLET_SPEED

    def update(self) -> bool:
        """Move bullet. Returns True if off-screen."""
        self.y -= self.speed
        return self.y < 0

class Game:
    """Main game controller."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Attack")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.game_over_font = pygame.font.Font(None, 72)
        self.background = self._load_background()
        self.sounds = self._load_sounds()
        self.reset()

    def _load_background(self) -> Optional[pygame.Surface]:
        """Load background image."""
        try:
            bg = pygame.image.load('bg.jpg')
            return pygame.transform.scale(bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            return None

    def _load_sounds(self) -> dict:
        """Load all sound effects."""
        sounds = {}
        try:
            mixer.music.load('background.wav')
            mixer.music.set_volume(0.5)
            sounds['background'] = True
        except:
            print("Could not load background music.")
        
        try:
            sounds['laser'] = mixer.Sound('laser.wav')
            sounds['explosion'] = mixer.Sound('explosion.wav')
        except:
            print("Could not load sound effects.")
        return sounds

    def reset(self) -> None:
        """Reset game state."""
        self.player = Player()
        self.bullets: List[Bullet] = []
        self.enemies: List[Enemy] = []
        self.score = 0
        self.game_over = False
        self.enemy_timer = pygame.time.get_ticks()
        if 'background' in self.sounds:
            mixer.music.play(-1)

    def handle_events(self) -> None:
        """Process keyboard and window events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self._fire_bullet()
                if event.key == pygame.K_r and self.game_over:
                    self.reset()

    def _fire_bullet(self) -> None:
        """Create a new bullet at player's position."""
        bullet = Bullet(
            x=self.player.x + self.player.width // 2 - 5,
            y=self.player.y
        )
        self.bullets.append(bullet)
        if 'laser' in self.sounds:
            self.sounds['laser'].play()

    def update(self) -> None:
        """Update game state."""
        if self.game_over:
            return

        self.player.update()
        
        # Spawn enemies
        if pygame.time.get_ticks() - self.enemy_timer > ENEMY_SPAWN_TIME:
            self.enemies.append(Enemy(random.randint(0, SCREEN_WIDTH - 50)))
            self.enemy_timer = pygame.time.get_ticks()

        # Update bullets
        for bullet in self.bullets[:]:
            if bullet.update():  # If bullet is off-screen
                self.bullets.remove(bullet)

        # Update enemies and check collisions
        for enemy in self.enemies[:]:
            if enemy.update():  # If enemy reached bottom
                self.game_over = True
            
            for bullet in self.bullets[:]:
                if bullet.get_rect().colliderect(enemy.get_rect()):
                    if 'explosion' in self.sounds:
                        self.sounds['explosion'].play()
                    self.bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 1
                    break

    def draw(self) -> None:
        """Render all game objects."""
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill((0, 0, 0))

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.player.draw(self.screen)
        self._draw_score()
        
        if self.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_score(self) -> None:
        """Render the score text."""
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

    def _draw_game_over(self) -> None:
        """Render game over screen."""
        game_over_text = self.game_over_font.render("GAME OVER", True, (255, 0, 0))
        self.screen.blit(game_over_text, (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))
        
        restart_text = self.font.render("Press R to restart", True, (255, 255, 255))
        self.screen.blit(restart_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 20))

    def run(self) -> None:
        """Main game loop."""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()



