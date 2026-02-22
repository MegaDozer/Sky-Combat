import pygame
import random
import math

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
BACKGROUND_TOP = (10, 22, 40)
BACKGROUND_BOTTOM = (5, 10, 20)
PLAYER_COLOR = (0, 212, 255)
ENEMY_COLOR = (255, 51, 51)
PLAYER_PROJECTILE = (255, 255, 0)
ENEMY_PROJECTILE = (255, 0, 102)
WHITE = (255, 255, 255)
CYAN_GLOW = (0, 212, 255)

# Game constants
PLAYER_SPEED = 5
ENEMY_SPEED = 2
PROJECTILE_SPEED = 7
ENEMY_PROJECTILE_SPEED = 4
SHOOT_COOLDOWN = 250
ENEMY_SPAWN_INTERVAL = 2000
MAX_ENEMIES = 10

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sky Combat")
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 24)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Draw plane shape
        points = [(20, 0), (40, 40), (20, 30), (0, 40)]
        pygame.draw.polygon(self.image, PLAYER_COLOR, points)
        pygame.draw.polygon(self.image, WHITE, points, 2)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.last_shot = 0
        self.lives = 3
        
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += PLAYER_SPEED
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += PLAYER_SPEED
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > SHOOT_COOLDOWN:
            self.last_shot = current_time
            return Projectile(self.rect.centerx, self.rect.top, True)
        return None

class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        # Draw inverted triangle
        points = [(0, 0), (40, 0), (20, 40)]
        pygame.draw.polygon(self.image, ENEMY_COLOR, points)
        pygame.draw.polygon(self.image, (255, 153, 51), points, 2)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - 40)
        self.rect.y = -40
        self.direction = random.choice([-1, 1])
        
    def update(self):
        self.rect.y += ENEMY_SPEED
        self.rect.x += self.direction * 0.5
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.direction *= -1

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, is_player):
        super().__init__()
        self.image = pygame.Surface((6, 15), pygame.SRCALPHA)
        color = PLAYER_PROJECTILE if is_player else ENEMY_PROJECTILE
        pygame.draw.ellipse(self.image, color, (0, 0, 6, 15))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.is_player = is_player
        
    def update(self):
        if self.is_player:
            self.rect.y -= PROJECTILE_SPEED
        else:
            self.rect.y += ENEMY_PROJECTILE_SPEED
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.particles = []
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': 30,
                'color': random.choice([(255, 153, 51), (255, 204, 0), (255, 100, 50)])
            })
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
    def update(self):
        self.image.fill((0, 0, 0, 0))
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] > 0:
                size = max(1, particle['life'] // 5)
                pygame.draw.circle(self.image, particle['color'], 
                                 (int(particle['x']), int(particle['y'])), size)
        if all(p['life'] <= 0 for p in self.particles):
            self.kill()

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 2)
        self.speed = random.uniform(0.5, 1.5)
        
    def update(self):
        self.y += self.speed
        if self.y > SCREEN_HEIGHT:
            self.y = 0
            self.x = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, surface):
        pygame.draw.circle(surface, (200, 200, 255), (self.x, self.y), self.size)

def draw_background():
    # Gradient background
    for y in range(SCREEN_HEIGHT):
        ratio = y / SCREEN_HEIGHT
        r = int(BACKGROUND_TOP[0] * (1 - ratio) + BACKGROUND_BOTTOM[0] * ratio)
        g = int(BACKGROUND_TOP[1] * (1 - ratio) + BACKGROUND_BOTTOM[1] * ratio)
        b = int(BACKGROUND_TOP[2] * (1 - ratio) + BACKGROUND_BOTTOM[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

def main():
    # Sprite groups
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    player_projectiles = pygame.sprite.Group()
    enemy_projectiles = pygame.sprite.Group()
    
    # Create player
    player = Player()
    all_sprites.add(player)
    
    # Create stars
    stars = [Star() for _ in range(50)]
    
    # Game variables
    score = 0
    game_over = False
    last_enemy_spawn = pygame.time.get_ticks()
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Restart game
                    main()
                    return
                elif event.key == pygame.K_SPACE and not game_over:
                    projectile = player.shoot()
                    if projectile:
                        all_sprites.add(projectile)
                        player_projectiles.add(projectile)
        
        if not game_over:
            # Spawn enemies
            current_time = pygame.time.get_ticks()
            if current_time - last_enemy_spawn > ENEMY_SPAWN_INTERVAL and len(enemies) < MAX_ENEMIES:
                enemy = Enemy()
                all_sprites.add(enemy)
                enemies.add(enemy)
                last_enemy_spawn = current_time
            
            # Enemy shooting
            for enemy in enemies:
                if random.random() < 0.01:
                    projectile = Projectile(enemy.rect.centerx, enemy.rect.bottom, False)
                    all_sprites.add(projectile)
                    enemy_projectiles.add(projectile)
            
            # Update all sprites
            all_sprites.update()
            for star in stars:
                star.update()
            
            # Collision: player projectiles hit enemies
            hits = pygame.sprite.groupcollide(enemies, player_projectiles, True, True)
            for hit in hits:
                score += 10
                explosion = Explosion(hit.rect.centerx, hit.rect.centery)
                all_sprites.add(explosion)
            
            # Collision: enemy projectiles hit player
            hits = pygame.sprite.spritecollide(player, enemy_projectiles, True)
            if hits:
                player.lives -= 1
                explosion = Explosion(player.rect.centerx, player.rect.centery)
                all_sprites.add(explosion)
                if player.lives <= 0:
                    game_over = True
            
            # Collision: enemies hit player
            hits = pygame.sprite.spritecollide(player, enemies, True)
            if hits:
                player.lives -= 1
                explosion = Explosion(player.rect.centerx, player.rect.centery)
                all_sprites.add(explosion)
                if player.lives <= 0:
                    game_over = True
        
        # Drawing
        draw_background()
        for star in stars:
            star.draw(screen)
        all_sprites.draw(screen)
        
        # HUD
        score_text = font_small.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        lives_text = font_small.render(f"Lives: {player.lives}", True, WHITE)
        lives_rect = lives_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(lives_text, lives_rect)
        
        if game_over:
            # Game over screen
            game_over_text = font_large.render("GAME OVER", True, CYAN_GLOW)
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            screen.blit(game_over_text, game_over_rect)
            
            final_score_text = font_small.render(f"Final Score: {score}", True, WHITE)
            final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            screen.blit(final_score_text, final_score_rect)
            
            restart_text = font_small.render("Press R to Restart", True, WHITE)
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen.blit(restart_text, restart_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
