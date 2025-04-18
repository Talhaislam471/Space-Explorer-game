import pygame
import random
import math
import os
import sys
import time

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
VICTORY = 3
PAUSE = 4
SHOP = 5
TUTORIAL = 6

class SpaceExplorer:
    def __init__(self):
        """Initialize the game with all necessary attributes and settings."""
        # Set up display for VS Code
        pygame.display.set_caption("Space Explorer")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Game state
        self.state = MENU
        self.level = 1
        self.score = 0
        self.lives = 3
        self.energy = 100
        self.max_energy = 100
        self.coins = 0
        self.game_time = 0
        
        # Load assets
        self.load_assets()
        
        # Sound effects (initialize pygame mixer)
        pygame.mixer.init()
        self.sounds = {
            'shoot': self.create_sound_effect(220, 0.1),
            'explosion': self.create_sound_effect(100, 0.3),
            'powerup': self.create_sound_effect(440, 0.2),
            'hit': self.create_sound_effect(150, 0.2)
        }
        
        # Player attributes
        self.player_pos = [WIDTH // 2, HEIGHT - 100]
        self.player_speed = 5
        self.player_bullets = []
        self.bullet_speed = 10
        self.bullet_damage = 10
        self.shoot_cooldown = 0
        self.shield_active = False
        self.shield_time = 0
        self.shield_cooldown = 0
        
        # Enemy attributes
        self.enemies = []
        self.enemy_bullets = []
        self.boss = None
        self.boss_health = 0
        self.boss_max_health = 0
        
        # Power-ups
        self.power_ups = []
        self.double_shot = False
        self.double_shot_time = 0
        
        # Stars background
        self.stars = []
        self.create_stars(100)
        
        # Particles
        self.particles = []
        
        # Shop items
        self.shop_items = [
            {"name": "Health Up", "cost": 50, "description": "Increase max health by 25"},
            {"name": "Speed Up", "cost": 30, "description": "Increase ship speed"},
            {"name": "Damage Up", "cost": 40, "description": "Increase bullet damage"},
            {"name": "Shield", "cost": 35, "description": "Activate shield for 10 seconds"},
            {"name": "Double Shot", "cost": 45, "description": "Fire two bullets at once for 15 seconds"}
        ]
        self.selected_item = 0
        
        # Button for menu
        self.buttons = {
            "start": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50),
            "shop": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50),
            "tutorial": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50),
            "quit": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 160, 200, 50),
            "resume": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 80, 200, 50),
            "menu": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50),
            "restart": pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 10, 200, 50),
            "back": pygame.Rect(WIDTH//2 - 100, HEIGHT - 100, 200, 50)
        }
        
        # Achievements
        self.achievements = {
            "first_kill": {"name": "First Blood", "description": "Destroy your first enemy", "unlocked": False},
            "collector": {"name": "Collector", "description": "Collect 10 power-ups", "unlocked": False, "count": 0},
            "survivor": {"name": "Survivor", "description": "Survive for 2 minutes", "unlocked": False},
            "boss_slayer": {"name": "Boss Slayer", "description": "Defeat a boss", "unlocked": False}
        }
        
        # Tutorial steps
        self.tutorial_step = 0
        self.tutorial_texts = [
            "Welcome to Space Explorer! This tutorial will guide you through the basics.",
            "Use the arrow keys or WASD to move your spaceship.",
            "Press SPACE to shoot. Destroy enemies to earn points and coins.",
            "Collect power-ups to enhance your ship. Blue = Energy, Green = Health, Yellow = Coins.",
            "Purple power-ups give special abilities like double shots or shields.",
            "Watch your energy bar! If it runs out, you can't shoot until it recharges.",
            "Defeat all enemies to advance to the next level. Every 5 levels has a boss!",
            "Visit the shop between levels to upgrade your ship.",
            "That's all! Good luck, space explorer!"
        ]
        
        # Sound effects and music
        self.sound_on = True
        
        # Background music
        self.background_music_playing = False

    def create_sound_effect(self, frequency, duration):
        """Create a simple sound effect using sine waves."""
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        
        # Generate a sine wave
        buf = bytearray()
        for i in range(num_samples):
            t = i / sample_rate  # Time in seconds
            # Simple sine wave with decay
            value = int(127 + 127 * math.sin(2 * math.pi * frequency * t) * (1 - t/duration))
            buf.append(value)
        
        # Create a Sound object from the buffer
        sound = pygame.mixer.Sound(buffer=bytes(buf))
        sound.set_volume(0.3)  # Set volume to 30%
        
        return sound

    def load_assets(self):
        """Load all game assets like images and fonts."""
        # Fonts
        self.title_font = pygame.font.SysFont('Arial', 48, bold=True)
        self.main_font = pygame.font.SysFont('Arial', 24)
        self.small_font = pygame.font.SysFont('Arial', 18)
        
        # Create placeholder images for player, enemies, bullets, etc.
        # In a real game, you'd load actual image files
        self.player_img = self.create_player_img()
        self.enemy_imgs = [
            self.create_enemy_img(RED),
            self.create_enemy_img(PURPLE),
            self.create_enemy_img(CYAN)
        ]
        self.boss_img = self.create_boss_img()
        self.bullet_img = self.create_bullet_img()
        self.shield_img = self.create_shield_img()
        
        # Power-up images
        self.powerup_imgs = {
            'health': self.create_powerup_img(GREEN),
            'energy': self.create_powerup_img(BLUE),
            'coin': self.create_powerup_img(YELLOW),
            'double_shot': self.create_powerup_img(PURPLE),
            'shield': self.create_powerup_img(CYAN)
        }

    def create_player_img(self):
        """Create a simple triangle ship for the player."""
        surf = pygame.Surface((30, 40), pygame.SRCALPHA)
        pygame.draw.polygon(surf, WHITE, [(15, 0), (0, 40), (30, 40)])
        pygame.draw.polygon(surf, BLUE, [(15, 5), (5, 35), (25, 35)])
        return surf
    
    def create_enemy_img(self, color):
        """Create a simple enemy ship."""
        surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(surf, color, [(15, 30), (0, 0), (30, 0)])
        return surf
    
    def create_boss_img(self):
        """Create a larger boss ship."""
        surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        pygame.draw.circle(surf, RED, (40, 40), 40)
        pygame.draw.circle(surf, YELLOW, (40, 40), 30)
        pygame.draw.circle(surf, RED, (40, 40), 20)
        pygame.draw.circle(surf, YELLOW, (40, 40), 10)
        return surf
    
    def create_bullet_img(self):
        """Create a simple bullet."""
        surf = pygame.Surface((6, 12), pygame.SRCALPHA)
        pygame.draw.rect(surf, YELLOW, (0, 0, 6, 12))
        return surf
    
    def create_shield_img(self):
        """Create a circular shield effect."""
        surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.circle(surf, (0, 100, 255, 128), (25, 25), 25)
        return surf
    
    def create_powerup_img(self, color):
        """Create a power-up image."""
        surf = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(surf, color, (10, 10), 10)
        pygame.draw.circle(surf, WHITE, (10, 10), 5)
        return surf
    
    def create_stars(self, count):
        """Create stars for the background."""
        for _ in range(count):
            self.stars.append([
                random.randint(0, WIDTH),    # x position
                random.randint(0, HEIGHT),   # y position
                random.random() * 2 + 1,     # size
                random.random() * 0.5 + 0.5  # brightness
            ])
    
    def move_stars(self):
        """Move the stars to create a scrolling effect."""
        for star in self.stars:
            star[1] += 0.5 * star[2]  # Move faster based on size
            if star[1] > HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, WIDTH)
    
    def draw_stars(self):
        """Draw the stars on the screen."""
        for star in self.stars:
            brightness = int(255 * star[3])
            color = (brightness, brightness, brightness)
            pygame.draw.circle(self.screen, color, (int(star[0]), int(star[1])), int(star[2]))
    
    def spawn_enemies(self):
        """Spawn enemies based on the current level."""
        # Clear any remaining enemies
        self.enemies = []
        
        # Number of enemies scales with level
        num_enemies = 5 + self.level * 2
        
        # Every 5 levels, spawn a boss instead
        if self.level % 5 == 0:
            self.boss = {
                'pos': [WIDTH // 2, 100],
                'direction': 1,
                'type': random.randint(0, 2),
                'attack_timer': 0
            }
            self.boss_health = 100 + (self.level // 5) * 50
            self.boss_max_health = self.boss_health
        else:
            # Spawn regular enemies in formation
            for i in range(num_enemies):
                enemy_type = random.randint(0, 2)
                row = i // 5
                col = i % 5
                
                self.enemies.append({
                    'pos': [100 + col * 150, 50 + row * 80],
                    'direction': 1,
                    'type': enemy_type,
                    'attack_timer': random.randint(0, 100)
                })
    
    def spawn_power_up(self, pos):
        """Spawn a power-up at the given position."""
        power_up_type = random.choices(
            ['health', 'energy', 'coin', 'double_shot', 'shield'],
            weights=[0.2, 0.3, 0.3, 0.1, 0.1],
            k=1
        )[0]
        
        self.power_ups.append({
            'pos': [pos[0], pos[1]],
            'type': power_up_type,
            'speed': 2
        })
    
    def add_particles(self, pos, color, count=10):
        """Add explosion particles at the given position."""
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 3)
            lifetime = random.uniform(30, 60)
            size = random.uniform(1, 3)
            
            self.particles.append({
                'pos': [pos[0], pos[1]],
                'vel': [math.cos(angle) * speed, math.sin(angle) * speed],
                'color': color,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'size': size
            })
    
    def update_particles(self):
        """Update and remove expired particles."""
        for particle in self.particles[:]:
            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]
            particle['lifetime'] -= 1
            
            if particle['lifetime'] <= 0:
                self.particles.remove(particle)
    
    def draw_particles(self):
        """Draw all active particles."""
        for particle in self.particles:
            alpha = int(255 * (particle['lifetime'] / particle['max_lifetime']))
            color = list(particle['color'])
            if len(color) == 3:
                color.append(alpha)
            else:
                color[3] = alpha
            
            pygame.draw.circle(
                self.screen, 
                color, 
                (int(particle['pos'][0]), int(particle['pos'][1])), 
                int(particle['size'])
            )
    
    def shoot(self):
        """Fire a bullet from the player's position."""
        if self.energy >= 5 and self.shoot_cooldown <= 0:
            # Single or double shot based on power-up
            if self.double_shot:
                self.player_bullets.append([self.player_pos[0] - 10, self.player_pos[1]])
                self.player_bullets.append([self.player_pos[0] + 10, self.player_pos[1]])
            else:
                self.player_bullets.append([self.player_pos[0], self.player_pos[1]])
            
            self.energy -= 5
            self.shoot_cooldown = 10
            
            # Play sound effect
            if self.sound_on:
                self.sounds['shoot'].play()
    
    def check_collisions(self):
        """Check for all collisions between game objects."""
        # Player bullets vs enemies
        for bullet in self.player_bullets[:]:
            # Check if bullet hit any enemy
            for enemy in self.enemies[:]:
                if (abs(bullet[0] - enemy['pos'][0]) < 20 and 
                    abs(bullet[1] - enemy['pos'][1]) < 20):
                    # Enemy hit
                    self.player_bullets.remove(bullet)
                    self.enemies.remove(enemy)
                    self.score += 10
                    self.coins += random.randint(1, 3)
                    
                    # Achievement: first kill
                    if not self.achievements["first_kill"]["unlocked"]:
                        self.achievements["first_kill"]["unlocked"] = True
                    
                    # Chance to spawn power-up
                    if random.random() < 0.2:
                        self.spawn_power_up(enemy['pos'])
                        
                    # Add explosion particles
                    self.add_particles(enemy['pos'], RED)
                    
                    # Play explosion sound
                    if self.sound_on:
                        self.sounds['explosion'].play()
                    break
            
            # Check if bullet hit boss
            if self.boss and bullet in self.player_bullets:  # Check if bullet wasn't already removed
                if (abs(bullet[0] - self.boss['pos'][0]) < 40 and 
                    abs(bullet[1] - self.boss['pos'][1]) < 40):
                    # Boss hit
                    if bullet in self.player_bullets:  # Check again to be safe
                        self.player_bullets.remove(bullet)
                    self.boss_health -= self.bullet_damage
                    self.score += 5
                    self.add_particles(bullet, YELLOW, 5)
                    
                    # Check if boss is defeated
                    if self.boss_health <= 0:
                        self.add_particles(self.boss['pos'], RED, 30)
                        self.boss = None
                        self.score += 100 * (self.level // 5)
                        self.coins += random.randint(20, 50)
                        
                        # Achievement: boss slayer
                        self.achievements["boss_slayer"]["unlocked"] = True
                        
                        # Spawn multiple power-ups
                        for _ in range(3):
                            offset_x = random.randint(-30, 30)
                            offset_y = random.randint(-30, 30)
                            pos = [self.player_pos[0] + offset_x, 100 + offset_y]
                            self.spawn_power_up(pos)
        
        # Enemy bullets vs player
        for bullet in self.enemy_bullets[:]:
            if (abs(bullet[0] - self.player_pos[0]) < 15 and 
                abs(bullet[1] - self.player_pos[1]) < 15):
                # Player hit
                self.enemy_bullets.remove(bullet)
                
                if not self.shield_active:
                    self.lives -= 1
                    self.add_particles(self.player_pos, BLUE, 15)
                    # Play hit sound
                    if self.sound_on:
                        self.sounds['hit'].play()
                    if self.lives <= 0:
                        self.state = GAME_OVER
                else:
                    # Shield absorbed the hit
                    self.add_particles(bullet, CYAN, 5)
        
        # Power-ups vs player
        for power_up in self.power_ups[:]:
            if (abs(power_up['pos'][0] - self.player_pos[0]) < 20 and 
                abs(power_up['pos'][1] - self.player_pos[1]) < 20):
                # Collect power-up
                self.power_ups.remove(power_up)
                
                # Apply power-up effect
                if power_up['type'] == 'health':
                    self.lives = min(self.lives + 1, 5)
                elif power_up['type'] == 'energy':
                    self.energy = self.max_energy
                elif power_up['type'] == 'coin':
                    self.coins += random.randint(5, 15)
                elif power_up['type'] == 'double_shot':
                    self.double_shot = True
                    self.double_shot_time = 900  # 15 seconds at 60 FPS
                elif power_up['type'] == 'shield':
                    self.shield_active = True
                    self.shield_time = 600  # 10 seconds at 60 FPS
                
                # Achievement: collector
                self.achievements["collector"]["count"] += 1
                if self.achievements["collector"]["count"] >= 10:
                    self.achievements["collector"]["unlocked"] = True
                
                # Add particles
                color = GREEN if power_up['type'] == 'health' else BLUE
                self.add_particles(power_up['pos'], color, 10)
                
                # Play power-up sound
                if self.sound_on:
                    self.sounds['powerup'].play()
    
    def update_game(self):
        """Update all game objects and states."""
        # Timer for achievements
        self.game_time += 1
        if self.game_time >= 7200 and not self.achievements["survivor"]["unlocked"]:  # 2 minutes at 60 FPS
            self.achievements["survivor"]["unlocked"] = True
        
        # Move stars
        self.move_stars()
        
        # Update cooldowns
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        
        # Energy regeneration
        if self.energy < self.max_energy:
            self.energy += 0.1
        
        # Power-up timers
        if self.double_shot:
            self.double_shot_time -= 1
            if self.double_shot_time <= 0:
                self.double_shot = False
        
        if self.shield_active:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.shield_active = False
                self.shield_cooldown = 1800  # 30 second cooldown
        
        if self.shield_cooldown > 0:
            self.shield_cooldown -= 1
        
        # Move player bullets
        for bullet in self.player_bullets[:]:
            bullet[1] -= self.bullet_speed
            if bullet[1] < 0:
                self.player_bullets.remove(bullet)
        
        # Move enemy bullets
        for bullet in self.enemy_bullets[:]:
            bullet[1] += 5
            if bullet[1] > HEIGHT:
                self.enemy_bullets.remove(bullet)
        
        # Move and update enemies
        for enemy in self.enemies[:]:
            # Move horizontally
            enemy['pos'][0] += enemy['direction'] * (2 + 0.1 * self.level)
            
            # Change direction if reaching screen edge
            if enemy['pos'][0] < 30 or enemy['pos'][0] > WIDTH - 30:
                enemy['direction'] *= -1
                enemy['pos'][1] += 20  # Move down a bit
            
            # Random attack
            enemy['attack_timer'] -= 1
            if enemy['attack_timer'] <= 0:
                # Fire at player
                self.enemy_bullets.append([enemy['pos'][0], enemy['pos'][1] + 15])
                enemy['attack_timer'] = random.randint(60, 120)
        
        # Update boss if present
        if self.boss:
            # Move horizontally
            self.boss['pos'][0] += self.boss['direction'] * 2
            
            # Change direction if reaching screen edge
            if self.boss['pos'][0] < 40 or self.boss['pos'][0] > WIDTH - 40:
                self.boss['direction'] *= -1
            
            # Boss attack pattern
            self.boss['attack_timer'] -= 1
            if self.boss['attack_timer'] <= 0:
                # Different attack patterns based on boss type
                if self.boss['type'] == 0:
                    # Spread shot
                    for angle in range(-2, 3):
                        self.enemy_bullets.append([
                            self.boss['pos'][0] + angle * 10, 
                            self.boss['pos'][1] + 20
                        ])
                elif self.boss['type'] == 1:
                    # Aimed shot
                    dx = self.player_pos[0] - self.boss['pos'][0]
                    self.enemy_bullets.append([
                        self.boss['pos'][0], 
                        self.boss['pos'][1] + 20
                    ])
                else:
                    # Double shot
                    self.enemy_bullets.append([self.boss['pos'][0] - 20, self.boss['pos'][1] + 10])
                    self.enemy_bullets.append([self.boss['pos'][0] + 20, self.boss['pos'][1] + 10])
                
                self.boss['attack_timer'] = random.randint(30, 60)
        
        # Move power-ups
        for power_up in self.power_ups[:]:
            power_up['pos'][1] += power_up['speed']
            if power_up['pos'][1] > HEIGHT:
                self.power_ups.remove(power_up)
        
        # Update particles
        self.update_particles()
        
        # Check for collisions
        self.check_collisions()
        
        # Check if level is complete
        if not self.enemies and not self.boss:
            self.level += 1
            self.state = SHOP
    
    def draw_game(self):
        """Draw all game elements to the screen."""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw stars
        self.draw_stars()
        
        # Draw particles
        self.draw_particles()
        
        # Draw player ship
        self.screen.blit(self.player_img, (self.player_pos[0] - 15, self.player_pos[1] - 20))
        
        # Draw shield if active
        if self.shield_active:
            self.screen.blit(self.shield_img, (self.player_pos[0] - 25, self.player_pos[1] - 25))
        
        # Draw player bullets
        for bullet in self.player_bullets:
            self.screen.blit(self.bullet_img, (bullet[0] - 3, bullet[1] - 6))
        
        # Draw enemies
        for enemy in self.enemies:
            enemy_img = self.enemy_imgs[enemy['type']]
            self.screen.blit(enemy_img, (enemy['pos'][0] - 15, enemy['pos'][1] - 15))
        
        # Draw boss if present
        if self.boss:
            self.screen.blit(self.boss_img, (self.boss['pos'][0] - 40, self.boss['pos'][1] - 40))
            
            # Draw boss health bar
            health_width = 80 * (self.boss_health / self.boss_max_health)
            pygame.draw.rect(self.screen, RED, (self.boss['pos'][0] - 40, self.boss['pos'][1] - 50, 80, 5))
            pygame.draw.rect(self.screen, GREEN, (self.boss['pos'][0] - 40, self.boss['pos'][1] - 50, health_width, 5))
        
        # Draw enemy bullets
        for bullet in self.enemy_bullets:
            pygame.draw.rect(self.screen, RED, (bullet[0] - 2, bullet[1] - 4, 4, 8))
        
        # Draw power-ups
        for power_up in self.power_ups:
            img = self.powerup_imgs[power_up['type']]
            self.screen.blit(img, (power_up['pos'][0] - 10, power_up['pos'][1] - 10))
        
        # Draw HUD
        # Lives
        life_text = self.main_font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(life_text, (10, 10))
        
        # Score
        score_text = self.main_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 40))
        
        # Level
        level_text = self.main_font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 70))
        
        # Coins
        coin_text = self.main_font.render(f"Coins: {self.coins}", True, YELLOW)
        self.screen.blit(coin_text, (WIDTH - 120, 10))
        
        # Energy bar
        pygame.draw.rect(self.screen, (50, 50, 50), (WIDTH - 160, 40, 150, 20))
        energy_width = max(0, 150 * (self.energy / self.max_energy))
        pygame.draw.rect(self.screen, BLUE, (WIDTH - 160, 40, energy_width, 20))
        energy_text = self.small_font.render("Energy", True, WHITE)
        self.screen.blit(energy_text, (WIDTH - 160, 65))
        
        # Power-up indicators
        if self.double_shot:
            double_text = self.small_font.render(f"Double Shot: {self.double_shot_time//60}s", True, PURPLE)
            self.screen.blit(double_text, (WIDTH - 160, 90))
        
        if self.shield_active:
            shield_text = self.small_font.render(f"Shield: {self.shield_time//60}s", True, CYAN)
            self.screen.blit(shield_text, (WIDTH - 160, 115))
        
    def draw_menu(self):
        """Draw the main menu screen."""
        # Clear screen and draw stars
        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Title
        title_text = self.title_font.render("SPACE EXPLORER", True, BLUE)
        self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        
        # Subtitle
        subtitle_text = self.main_font.render("An Epic Space Adventure", True, WHITE)
        self.screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, 160))
        
        # Draw buttons
        pygame.draw.rect(self.screen, BLUE, self.buttons["start"])
        pygame.draw.rect(self.screen, PURPLE, self.buttons["shop"])
        pygame.draw.rect(self.screen, GREEN, self.buttons["tutorial"])
        pygame.draw.rect(self.screen, RED, self.buttons["quit"])
        
        # Button text
        start_text = self.main_font.render("Start Game", True, WHITE)
        self.screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, HEIGHT//2 - 35))
        
        shop_text = self.main_font.render("Shop", True, WHITE)
        self.screen.blit(shop_text, (WIDTH//2 - shop_text.get_width()//2, HEIGHT//2 + 35))
        
        tutorial_text = self.main_font.render("Tutorial", True, WHITE)
        self.screen.blit(tutorial_text, (WIDTH//2 - tutorial_text.get_width()//2, HEIGHT//2 + 105))
        
        quit_text = self.main_font.render("Quit", True, WHITE)
        self.screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 175))
        
        # Draw achievements
        achievement_text = self.main_font.render("Achievements:", True, YELLOW)
        self.screen.blit(achievement_text, (20, HEIGHT - 120))
        
        y_offset = HEIGHT - 90
        for achievement in self.achievements.values():
            status = "✓" if achievement["unlocked"] else "✗"
            color = GREEN if achievement["unlocked"] else RED
            text = self.small_font.render(f"{status} {achievement['name']}", True, color)
            self.screen.blit(text, (30, y_offset))
            y_offset += 20
    
    def draw_shop(self):
        """Draw the shop screen."""
        # Clear screen and draw stars
        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Title
        title_text = self.title_font.render("SHOP", True, YELLOW)
        self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        # Player stats
        stats_text = self.main_font.render(f"Coins: {self.coins} | Level: {self.level} | Lives: {self.lives}", True, WHITE)
        self.screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, 120))
        
        # Shop items
        for i, item in enumerate(self.shop_items):
            # Item box
            color = BLUE if i == self.selected_item else (50, 50, 50)
            pygame.draw.rect(self.screen, color, (WIDTH//2 - 150, 180 + i*60, 300, 50))
            
            # Item name and cost
            name_text = self.main_font.render(item["name"], True, WHITE)
            self.screen.blit(name_text, (WIDTH//2 - 140, 190 + i*60))
            
            cost_text = self.main_font.render(f"{item['cost']} coins", True, YELLOW)
            self.screen.blit(cost_text, (WIDTH//2 + 50, 190 + i*60))
            
            # Item description
            desc_text = self.small_font.render(item["description"], True, WHITE)
            self.screen.blit(desc_text, (WIDTH//2 - 140, 215 + i*60))
        
        # Instructions
        instr_text = self.small_font.render("Use UP/DOWN to select, ENTER to buy, ESC to return to game", True, WHITE)
        self.screen.blit(instr_text, (WIDTH//2 - instr_text.get_width()//2, HEIGHT - 50))
    
    def draw_game_over(self):
        """Draw the game over screen."""
        # Clear screen and draw stars
        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Title
        title_text = self.title_font.render("GAME OVER", True, RED)
        self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        
        # Score
        score_text = self.main_font.render(f"Final Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 180))
        
        # Level reached
        level_text = self.main_font.render(f"Level Reached: {self.level}", True, WHITE)
        self.screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, 220))
        
        # Buttons
        pygame.draw.rect(self.screen, GREEN, self.buttons["restart"])
        pygame.draw.rect(self.screen, BLUE, self.buttons["menu"])
        
        # Button text
        restart_text = self.main_font.render("Play Again", True, WHITE)
        self.screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 - 10 + 15))
        
        menu_text = self.main_font.render("Main Menu", True, WHITE)
        self.screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 20 + 15))
    
    def draw_pause(self):
        """Draw the pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Pause title
        title_text = self.title_font.render("PAUSED", True, WHITE)
        self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 100))
        
        # Buttons
        pygame.draw.rect(self.screen, GREEN, self.buttons["resume"])
        pygame.draw.rect(self.screen, BLUE, self.buttons["menu"])
        
        # Button text
        resume_text = self.main_font.render("Resume Game", True, WHITE)
        self.screen.blit(resume_text, (WIDTH//2 - resume_text.get_width()//2, HEIGHT//2 - 65))
        
        menu_text = self.main_font.render("Main Menu", True, WHITE)
        self.screen.blit(menu_text, (WIDTH//2 - menu_text.get_width()//2, HEIGHT//2 + 35))
    
    def draw_tutorial(self):
        """Draw the tutorial screen."""
        # Clear screen and draw stars
        self.screen.fill(BLACK)
        self.draw_stars()
        
        # Title
        title_text = self.title_font.render("TUTORIAL", True, GREEN)
        self.screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, 50))
        
        # Current tutorial step
        step_text = self.tutorial_texts[self.tutorial_step]
        
        # Wrap text
        words = step_text.split(' ')
        lines = []
        line = ""
        for word in words:
            test_line = line + word + " "
            if self.main_font.size(test_line)[0] < WIDTH - 100:
                line = test_line
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)
        
        # Draw wrapped text
        y = 150
        for line in lines:
            text = self.main_font.render(line, True, WHITE)
            self.screen.blit(text, (50, y))
            y += 30
        
        # Navigation instructions
        nav_text = self.small_font.render(
            f"Step {self.tutorial_step + 1}/{len(self.tutorial_texts)} - Press LEFT/RIGHT to navigate, ESC to exit", 
            True, 
            WHITE
        )
        self.screen.blit(nav_text, (WIDTH//2 - nav_text.get_width()//2, HEIGHT - 50))
        
        # Back button
        if self.tutorial_step == len(self.tutorial_texts) - 1:
            pygame.draw.rect(self.screen, BLUE, self.buttons["back"])
            back_text = self.main_font.render("Back to Menu", True, WHITE)
            self.screen.blit(back_text, (WIDTH//2 - back_text.get_width()//2, HEIGHT - 85))
    
    def handle_shop_input(self, event):
        """Handle input for the shop screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Return to game
                self.state = PLAYING
                self.spawn_enemies()
            elif event.key == pygame.K_UP:
                # Move selection up
                self.selected_item = max(0, self.selected_item - 1)
            elif event.key == pygame.K_DOWN:
                # Move selection down
                self.selected_item = min(len(self.shop_items) - 1, self.selected_item + 1)
            elif event.key == pygame.K_RETURN:
                # Try to buy selected item
                item = self.shop_items[self.selected_item]
                if self.coins >= item["cost"]:
                    # Purchase successful
                    self.coins -= item["cost"]
                    
                    # Apply item effect
                    if item["name"] == "Health Up":
                        self.lives = min(self.lives + 1, 5)
                    elif item["name"] == "Speed Up":
                        self.player_speed += 1
                    elif item["name"] == "Damage Up":
                        self.bullet_damage += 5
                    elif item["name"] == "Shield":
                        self.shield_active = True
                        self.shield_time = 600  # 10 seconds
                    elif item["name"] == "Double Shot":
                        self.double_shot = True
                        self.double_shot_time = 900  # 15 seconds
                    
                    # Play power-up sound
                    if self.sound_on:
                        self.sounds['powerup'].play()
    
    def handle_menu_input(self, event):
        """Handle input for the main menu screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.buttons["start"].collidepoint(mouse_pos):
                # Start game
                self.reset_game()
                self.state = PLAYING
                self.spawn_enemies()
            elif self.buttons["shop"].collidepoint(mouse_pos):
                # Go to shop
                self.state = SHOP
            elif self.buttons["tutorial"].collidepoint(mouse_pos):
                # Go to tutorial
                self.state = TUTORIAL
                self.tutorial_step = 0
            elif self.buttons["quit"].collidepoint(mouse_pos):
                # Quit game
                return False
        
        return True
    
    def handle_game_over_input(self, event):
        """Handle input for the game over screen."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.buttons["restart"].collidepoint(mouse_pos):
                # Restart game
                self.reset_game()
                self.state = PLAYING
                self.spawn_enemies()
            elif self.buttons["menu"].collidepoint(mouse_pos):
                # Return to main menu
                self.state = MENU
    
    def handle_pause_input(self, event):
        """Handle input for the pause screen."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            # Resume game
            self.state = PLAYING
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.buttons["resume"].collidepoint(mouse_pos):
                # Resume game
                self.state = PLAYING
            elif self.buttons["menu"].collidepoint(mouse_pos):
                # Return to main menu
                self.state = MENU
    
    def handle_tutorial_input(self, event):
        """Handle input for the tutorial screen."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                # Exit tutorial
                self.state = MENU
            elif event.key == pygame.K_LEFT:
                # Previous step
                self.tutorial_step = max(0, self.tutorial_step - 1)
            elif event.key == pygame.K_RIGHT:
                # Next step
                self.tutorial_step = min(len(self.tutorial_texts) - 1, self.tutorial_step + 1)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            
            if self.tutorial_step == len(self.tutorial_texts) - 1 and self.buttons["back"].collidepoint(mouse_pos):
                # Return to main menu from last step
                self.state = MENU
    
    def handle_game_input(self):
        """Handle input for the main gameplay."""
        keys = pygame.key.get_pressed()
        
        # Movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player_pos[0] = max(30, self.player_pos[0] - self.player_speed)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player_pos[0] = min(WIDTH - 30, self.player_pos[0] + self.player_speed)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player_pos[1] = max(50, self.player_pos[1] - self.player_speed)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.player_pos[1] = min(HEIGHT - 50, self.player_pos[1] + self.player_speed)
        
        # Shooting
        if keys[pygame.K_SPACE]:
            self.shoot()
    
    def reset_game(self):
        """Reset the game to initial state."""
        self.level = 1
        self.score = 0
        self.lives = 3
        self.energy = 100
        self.player_pos = [WIDTH // 2, HEIGHT - 100]
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.boss = None
        self.power_ups = []
        self.particles = []
        self.double_shot = False
        self.shield_active = False
        self.game_time = 0
    
    def run_frame(self):
        """Run a single frame of the game."""
        # Process events
        running = True
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE and self.state == PLAYING:
                    self.state = PAUSE
            
            # Handle state-specific input
            if self.state == MENU:
                running = self.handle_menu_input(event)
            elif self.state == GAME_OVER:
                self.handle_game_over_input(event)
            elif self.state == PAUSE:
                self.handle_pause_input(event)
            elif self.state == SHOP:
                self.handle_shop_input(event)
            elif self.state == TUTORIAL:
                self.handle_tutorial_input(event)
        
        # Update and draw based on game state
        if self.state == PLAYING:
            self.handle_game_input()
            self.update_game()
            self.draw_game()
        elif self.state == MENU:
            self.draw_menu()
        elif self.state == GAME_OVER:
            self.draw_game_over()
        elif self.state == PAUSE:
            self.draw_game()
            self.draw_pause()
        elif self.state == SHOP:
            self.draw_shop()
        elif self.state == TUTORIAL:
            self.draw_tutorial()
        
        # Cap framerate
        self.clock.tick(FPS)
        
        # Update display
        pygame.display.flip()
        
        return running
    
    def run(self):
        """Main game loop for standalone pygame."""
        running = True
        while running:
            running = self.run_frame()
        
        pygame.quit()

# Main execution
if __name__ == "__main__":
    game = SpaceExplorer()
    game.run()
