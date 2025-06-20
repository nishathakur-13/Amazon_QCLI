import pygame
import random
import sys
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# Game constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# Player settings
PLAYER_WIDTH = 50
PLAYER_HEIGHT = 40
PLAYER_SPEED = 5

# Bullet settings
BULLET_WIDTH = 5
BULLET_HEIGHT = 10
BULLET_SPEED = 7

# Asteroid settings
ASTEROID_WIDTH = 40
ASTEROID_HEIGHT = 40
ASTEROID_BASE_MIN_SPEED = 2
ASTEROID_BASE_MAX_SPEED = 5
ASTEROID_BASE_SPAWN_RATE = 30  # Lower = more frequent spawning

# Level system settings
POINTS_PER_LEVEL = 100  # Points needed to advance to next level
MAX_LEVEL = 10  # Maximum difficulty level

# Power-up settings
POWERUP_SPAWN_CHANCE = 0.005  # Chance per frame to spawn a power-up (0.5%)
POWERUP_FALL_SPEED = 3
POWERUP_WIDTH = 30
POWERUP_HEIGHT = 30
SHIELD_DURATION = 300  # 5 seconds at 60 FPS
RAPID_FIRE_DURATION = 300  # 5 seconds at 60 FPS
RAPID_FIRE_COOLDOWN = 5  # Frames between shots during rapid fire

# Enemy ship settings
ENEMY_SHIP_WIDTH = 35
ENEMY_SHIP_HEIGHT = 30
ENEMY_SHIP_SPEED = 2
ENEMY_SHIP_SPAWN_CHANCE = 0.008  # Chance per frame to spawn enemy ship
ENEMY_BULLET_SPEED = 4
ENEMY_SHOOT_COOLDOWN = 90  # Frames between enemy shots

# Audio settings
ENABLE_AUDIO = True  # Set to False to disable audio

def create_audio_effects():
    """Create audio effects using numpy arrays if available"""
    sounds = {}
    
    try:
        import numpy as np
        
        # Create explosion sound (noise burst)
        sample_rate = 22050
        duration = 0.3  # 0.3 seconds
        frames = int(duration * sample_rate)
        
        # Generate explosion noise
        explosion_data = np.random.uniform(-1, 1, frames)
        # Apply fade out envelope
        fade_out = np.linspace(1, 0, frames)
        explosion_data *= fade_out
        # Scale to 16-bit range
        explosion_data = (explosion_data * 16000).astype(np.int16)
        
        # Convert to stereo
        stereo_explosion = np.column_stack((explosion_data, explosion_data))
        sounds['explosion'] = pygame.sndarray.make_sound(stereo_explosion)
        
        # Create shooting sound (quick beep)
        shoot_duration = 0.1
        shoot_frames = int(shoot_duration * sample_rate)
        t = np.linspace(0, shoot_duration, shoot_frames)
        
        # Create a quick rising tone
        frequency = 800 + t * 2000  # Rising frequency
        amplitude = np.linspace(1, 0, shoot_frames)  # Fade out
        shoot_wave = amplitude * np.sin(2 * np.pi * frequency * t)
        shoot_data = (shoot_wave * 8000).astype(np.int16)
        
        # Convert to stereo
        stereo_shoot = np.column_stack((shoot_data, shoot_data))
        sounds['shoot'] = pygame.sndarray.make_sound(stereo_shoot)
        
        # Create simple background music
        music_duration = 4  # 4 seconds loop
        music_frames = int(music_duration * sample_rate)
        t = np.linspace(0, music_duration, music_frames)
        
        # Create a simple chord progression
        notes = [261.63, 293.66, 329.63, 349.23]  # C, D, E, F
        music_wave = np.zeros(music_frames)
        
        for i, freq in enumerate(notes):
            start_frame = i * music_frames // len(notes)
            end_frame = (i + 1) * music_frames // len(notes)
            note_t = t[start_frame:end_frame] - t[start_frame]
            
            # Create note with harmonics
            note_wave = (np.sin(2 * np.pi * freq * note_t) * 0.5 +
                        np.sin(2 * np.pi * freq * 2 * note_t) * 0.3 +
                        np.sin(2 * np.pi * freq * 3 * note_t) * 0.2)
            
            # Apply envelope
            envelope = np.ones_like(note_t)
            fade_samples = len(note_t) // 10
            if fade_samples > 0:
                envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
                envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
            
            music_wave[start_frame:end_frame] = note_wave * envelope
        
        # Scale and convert to stereo
        music_data = (music_wave * 3000).astype(np.int16)
        stereo_music = np.column_stack((music_data, music_data))
        sounds['music'] = pygame.sndarray.make_sound(stereo_music)
        
        # Create power-up pickup sound
        pickup_duration = 0.2
        pickup_frames = int(pickup_duration * sample_rate)
        t = np.linspace(0, pickup_duration, pickup_frames)
        
        # Create a pleasant ascending tone
        frequency = 440 + t * 880  # Rising from A4 to A5
        amplitude = np.exp(-t * 3)  # Exponential decay
        pickup_wave = amplitude * np.sin(2 * np.pi * frequency * t)
        pickup_data = (pickup_wave * 12000).astype(np.int16)
        
        # Convert to stereo
        stereo_pickup = np.column_stack((pickup_data, pickup_data))
        sounds['pickup'] = pygame.sndarray.make_sound(stereo_pickup)
        
        print("Audio effects created successfully!")
        return sounds
        
    except ImportError:
        print("NumPy not available - audio effects disabled")
        return {}
    except Exception as e:
        print(f"Could not create audio effects: {e}")
        return {}

class Particle:
    """Simple particle for explosion effects"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = 30
        self.max_life = 30
        self.color = random.choice([RED, ORANGE, YELLOW])
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.vy += 0.1  # Gravity
    
    def draw(self, screen):
        if self.life > 0:
            alpha = self.life / self.max_life
            size = int(3 * alpha)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
    
    def is_alive(self):
        return self.life > 0

class EnemyBullet:
    """Enemy bullet class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 4
        self.height = 8
        self.speed = ENEMY_BULLET_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self):
        """Update enemy bullet position"""
        self.y += self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        """Draw the enemy bullet"""
        pygame.draw.rect(screen, RED, self.rect)
        # Add glow effect
        pygame.draw.rect(screen, ORANGE, (self.rect.x - 1, self.rect.y - 1, self.width + 2, self.height + 2), 1)
    
    def is_off_screen(self):
        """Check if bullet is off screen"""
        return self.y > SCREEN_HEIGHT

class EnemyShip:
    """Enemy ship class that shoots at the player"""
    def __init__(self, x, y, level=1):
        self.x = x
        self.y = y
        self.width = ENEMY_SHIP_WIDTH
        self.height = ENEMY_SHIP_HEIGHT
        self.speed = ENEMY_SHIP_SPEED + (level - 1) * 0.5  # Slightly faster at higher levels
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.level = level
        self.shoot_timer = random.randint(30, ENEMY_SHOOT_COOLDOWN)  # Random initial delay
        self.direction = random.choice([-1, 1])  # Movement direction
        self.move_timer = 0
    
    def update(self):
        """Update enemy ship position and shooting"""
        # Move down
        self.y += self.speed
        self.rect.y = self.y
        
        # Side-to-side movement
        self.move_timer += 1
        if self.move_timer > 60:  # Change direction every second
            self.direction *= -1
            self.move_timer = 0
        
        # Move horizontally
        self.x += self.direction * 1
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.direction *= -1
        self.rect.x = self.x
        
        # Update shoot timer
        self.shoot_timer -= 1
    
    def can_shoot(self):
        """Check if enemy can shoot"""
        return self.shoot_timer <= 0
    
    def shoot(self):
        """Create a bullet aimed at player position"""
        self.shoot_timer = ENEMY_SHOOT_COOLDOWN - (self.level - 1) * 10  # Shoot faster at higher levels
        bullet_x = self.x + self.width // 2 - 2
        bullet_y = self.y + self.height
        return EnemyBullet(bullet_x, bullet_y)
    
    def draw(self, screen):
        """Draw the enemy ship"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Draw enemy ship as an inverted triangle (pointing down)
        points = [
            (center_x, self.y + self.height),  # Bottom point
            (self.x, self.y),                  # Top left
            (self.x + self.width, self.y)      # Top right
        ]
        
        # Color based on level
        ship_color = (min(255, 150 + self.level * 15), 0, 0)  # Gets redder with level
        pygame.draw.polygon(screen, ship_color, points)
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Add engine glow
        pygame.draw.circle(screen, ORANGE, (center_x, self.y), 3)
        
        # Add level indicator for high-level ships
        if self.level > 2:
            level_text = pygame.font.Font(None, 16).render(str(self.level), True, WHITE)
            text_rect = level_text.get_rect(center=(center_x, center_y))
            screen.blit(level_text, text_rect)
    
    def is_off_screen(self):
        """Check if enemy ship is off screen"""
        return self.y > SCREEN_HEIGHT

class PowerUp:
    """Power-up class for special abilities"""
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.width = POWERUP_WIDTH
        self.height = POWERUP_HEIGHT
        self.speed = POWERUP_FALL_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.type = powerup_type  # 'shield' or 'rapid_fire'
        self.pulse = 0  # For visual pulsing effect
    
    def update(self):
        """Update power-up position"""
        self.y += self.speed
        self.rect.y = self.y
        self.pulse += 0.2
    
    def draw(self, screen):
        """Draw the power-up with visual effects"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Pulsing effect
        pulse_size = int(3 * math.sin(self.pulse))
        
        if self.type == 'shield':
            # Draw shield power-up (blue circle with cross)
            pygame.draw.circle(screen, BLUE, (center_x, center_y), self.width // 2 + pulse_size)
            pygame.draw.circle(screen, WHITE, (center_x, center_y), self.width // 2 + pulse_size, 3)
            # Draw shield symbol (cross)
            pygame.draw.line(screen, WHITE, (center_x - 8, center_y), (center_x + 8, center_y), 3)
            pygame.draw.line(screen, WHITE, (center_x, center_y - 8), (center_x, center_y + 8), 3)
            
        elif self.type == 'rapid_fire':
            # Draw rapid fire power-up (red triangle with arrows)
            pygame.draw.circle(screen, RED, (center_x, center_y), self.width // 2 + pulse_size)
            pygame.draw.circle(screen, WHITE, (center_x, center_y), self.width // 2 + pulse_size, 3)
            # Draw rapid fire symbol (up arrows)
            points1 = [(center_x - 5, center_y + 5), (center_x - 5, center_y - 5), (center_x - 8, center_y - 2)]
            points2 = [(center_x + 5, center_y + 5), (center_x + 5, center_y - 5), (center_x + 8, center_y - 2)]
            pygame.draw.polygon(screen, WHITE, points1)
            pygame.draw.polygon(screen, WHITE, points2)
    
    def is_off_screen(self):
        """Check if power-up is off screen"""
        return self.y > SCREEN_HEIGHT

class Player:
    """Player spaceship class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # Power-up states
        self.has_shield = False
        self.shield_timer = 0
        self.rapid_fire = False
        self.rapid_fire_timer = 0
        self.shoot_cooldown = 0
    
    def move_left(self):
        """Move player left"""
        if self.x > 0:
            self.x -= self.speed
            self.rect.x = self.x
    
    def move_right(self):
        """Move player right"""
        if self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
            self.rect.x = self.x
    
    def update(self):
        """Update player state including power-ups"""
        # Update shield
        if self.has_shield:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.has_shield = False
        
        # Update rapid fire
        if self.rapid_fire:
            self.rapid_fire_timer -= 1
            if self.rapid_fire_timer <= 0:
                self.rapid_fire = False
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def can_shoot(self):
        """Check if player can shoot based on rapid fire state"""
        return self.shoot_cooldown <= 0
    
    def shoot(self):
        """Handle shooting with appropriate cooldown"""
        if self.rapid_fire:
            self.shoot_cooldown = RAPID_FIRE_COOLDOWN
        else:
            self.shoot_cooldown = 15  # Normal shooting cooldown
    
    def activate_shield(self):
        """Activate shield power-up"""
        self.has_shield = True
        self.shield_timer = SHIELD_DURATION
    
    def activate_rapid_fire(self):
        """Activate rapid fire power-up"""
        self.rapid_fire = True
        self.rapid_fire_timer = RAPID_FIRE_DURATION
    
    def take_damage(self):
        """Handle taking damage - returns True if player dies"""
        if self.has_shield:
            self.has_shield = False
            self.shield_timer = 0
            return False  # Shield absorbed the hit
        else:
            return True  # Player dies
    
    def draw(self, screen):
        """Draw the player spaceship"""
        # Draw spaceship as a triangle with more detail
        points = [
            (self.x + self.width // 2, self.y),  # Top point
            (self.x, self.y + self.height),      # Bottom left
            (self.x + self.width, self.y + self.height)  # Bottom right
        ]
        pygame.draw.polygon(screen, GREEN, points)
        # Add a small rectangle for the body
        pygame.draw.rect(screen, BLUE, (self.x + 15, self.y + 20, 20, 15))
        # Add engine glow
        pygame.draw.circle(screen, YELLOW, (self.x + self.width // 2, self.y + self.height), 5)

class Bullet:
    """Bullet class"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = BULLET_WIDTH
        self.height = BULLET_HEIGHT
        self.speed = BULLET_SPEED
        self.rect = pygame.Rect(x, y, self.width, self.height)
    
    def update(self):
        """Update bullet position"""
        self.y -= self.speed
        self.rect.y = self.y
    
    def draw(self, screen):
        """Draw the bullet with a glow effect"""
        pygame.draw.rect(screen, YELLOW, self.rect)
        # Add glow effect
        pygame.draw.rect(screen, WHITE, (self.rect.x - 1, self.rect.y - 1, self.width + 2, self.height + 2), 1)
    
    def is_off_screen(self):
        """Check if bullet is off screen"""
        return self.y < 0

class Asteroid:
    """Asteroid enemy class"""
    def __init__(self, x, y, level=1):
        self.x = x
        self.y = y
        self.width = ASTEROID_WIDTH
        self.height = ASTEROID_HEIGHT
        
        # Speed increases with level
        speed_multiplier = 1 + (level - 1) * 0.3  # 30% speed increase per level
        min_speed = int(ASTEROID_BASE_MIN_SPEED * speed_multiplier)
        max_speed = int(ASTEROID_BASE_MAX_SPEED * speed_multiplier)
        self.speed = random.randint(min_speed, max_speed)
        
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5) * speed_multiplier
        self.level = level
        
        # Visual changes based on level
        self.color_intensity = min(255, 128 + level * 15)  # Gets redder with higher levels
    
    def update(self):
        """Update asteroid position"""
        self.y += self.speed
        self.rect.y = self.y
        self.rotation += self.rotation_speed
    
    def draw(self, screen):
        """Draw the asteroid with rotation effect and level-based coloring"""
        center_x = self.x + self.width // 2
        center_y = self.y + self.height // 2
        
        # Color changes based on level - higher levels are more red/dangerous looking
        base_color = (min(255, GRAY[0] + self.level * 10), 
                     max(0, GRAY[1] - self.level * 5), 
                     max(0, GRAY[2] - self.level * 5))
        outline_color = (min(255, RED[0]), 
                        max(0, RED[1] - self.level * 10), 
                        max(0, RED[2] - self.level * 10))
        
        # Draw asteroid as an irregular shape
        pygame.draw.circle(screen, base_color, (center_x, center_y), self.width // 2)
        pygame.draw.circle(screen, outline_color, (center_x, center_y), self.width // 2, 3)
        
        # Add some detail lines for rotation effect
        import math
        for i in range(3):
            angle = self.rotation + i * 120
            end_x = center_x + int((self.width // 3) * math.cos(math.radians(angle)))
            end_y = center_y + int((self.width // 3) * math.sin(math.radians(angle)))
            pygame.draw.line(screen, WHITE, (center_x, center_y), (end_x, end_y), 2)
        
        # Add level indicator for high-level asteroids
        if self.level > 3:
            level_text = pygame.font.Font(None, 20).render(str(self.level), True, WHITE)
            text_rect = level_text.get_rect(center=(center_x, center_y))
            screen.blit(level_text, text_rect)
    
    def is_off_screen(self):
        """Check if asteroid is off screen"""
        return self.y > SCREEN_HEIGHT

class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Shooter - Enhanced Edition")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.small_font = pygame.font.Font(None, 24)
        
        # Initialize audio
        self.sounds = {}
        self.audio_enabled = ENABLE_AUDIO
        self.music_channel = None
        self.music_playing = False
        
        if self.audio_enabled:
            print("Loading audio...")
            self.sounds = create_audio_effects()
            
            # Start background music if available
            if 'music' in self.sounds:
                self.music_channel = pygame.mixer.Channel(0)
                self.music_channel.play(self.sounds['music'], loops=-1)
                self.music_channel.set_volume(0.2)  # Lower volume for background
                self.music_playing = True
                print("Background music started!")
            
            if self.sounds:
                print(f"Sound effects loaded: {list(self.sounds.keys())}")
        
        # Game state
        self.running = True
        self.game_over = False
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.previous_level = 1
        
        # Game objects
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.bullets = []
        self.asteroids = []
        self.powerups = []
        self.enemy_ships = []
        self.enemy_bullets = []
        self.particles = []
        self.asteroid_spawn_timer = 0
        
        # Visual effects
        self.stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(50)]
        
        # Level system
        self.level_up_timer = 0  # Timer for level up display
        self.show_level_up = False
    
    def get_current_level(self):
        """Calculate current level based on score"""
        return min(MAX_LEVEL, (self.score // POINTS_PER_LEVEL) + 1)
    
    def get_spawn_rate(self):
        """Get asteroid spawn rate based on current level"""
        # Spawn rate decreases (more frequent) as level increases
        level = self.get_current_level()
        spawn_rate = max(10, ASTEROID_BASE_SPAWN_RATE - (level - 1) * 2)  # Minimum spawn rate of 10
        return spawn_rate
    
    def check_level_up(self):
        """Check if player has leveled up"""
        current_level = self.get_current_level()
        if current_level > self.level:
            self.level = current_level
            self.show_level_up = True
            self.level_up_timer = 120  # Show level up message for 2 seconds at 60 FPS
            
            # Play a special sound for level up (reuse explosion sound with different volume)
            if self.audio_enabled and 'explosion' in self.sounds:
                level_up_channel = pygame.mixer.Channel(4)
                level_up_channel.play(self.sounds['explosion'])
                level_up_channel.set_volume(0.3)  # Quieter for level up
            
            print(f"Level Up! Now at Level {self.level}")
            return True
        return False
    
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_s) and not self.game_over:  # Add support for 'S' key
                    # Shoot bullet
                    bullet_x = self.player.x + self.player.width // 2 - BULLET_WIDTH // 2
                    bullet_y = self.player.y
                    self.bullets.append(Bullet(bullet_x, bullet_y))
                    
                    # Play shooting sound
                    if self.audio_enabled and 'shoot' in self.sounds:
                        shoot_channel = pygame.mixer.Channel(1)
                        shoot_channel.play(self.sounds['shoot'])
                        shoot_channel.set_volume(0.4)
                        
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()
                elif event.key == pygame.K_m:
                    # Toggle music
                    if self.music_channel and 'music' in self.sounds:
                        if self.music_playing:
                            self.music_channel.stop()
                            self.music_playing = False
                            print("Music stopped")
                        else:
                            self.music_channel.play(self.sounds['music'], loops=-1)
                            self.music_channel.set_volume(0.2)
                            self.music_playing = True
                            print("Music started")
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_d) and not self.game_over:  # Add support for 'D' key
                    # Shoot bullet
                    bullet_x = self.player.x + self.player.width // 2 - BULLET_WIDTH // 2
                    bullet_y = self.player.y
                    self.bullets.append(Bullet(bullet_x, bullet_y))
                    
                    # Play shooting sound
                    if self.audio_enabled and 'shoot' in self.sounds:
                        shoot_channel = pygame.mixer.Channel(1)
                        shoot_channel.play(self.sounds['shoot'])
                        shoot_channel.set_volume(0.4)
                        
                elif event.key == pygame.K_r and self.game_over:
                    # Restart game
                    self.restart_game()
                elif event.key == pygame.K_m:
                    # Toggle music
                    if self.music_channel and 'music' in self.sounds:
                        if self.music_playing:
                            self.music_channel.stop()
                            self.music_playing = False
                            print("Music stopped")
                        else:
                            self.music_channel.play(self.sounds['music'], loops=-1)
                            self.music_channel.set_volume(0.2)
                            self.music_playing = True
                            print("Music started")
    
    def update(self):
        """Update game state"""
        if self.game_over:
            # Update particles even when game over
            for particle in self.particles[:]:
                particle.update()
                if not particle.is_alive():
                    self.particles.remove(particle)
            
            # Update level up timer
            if self.show_level_up:
                self.level_up_timer -= 1
                if self.level_up_timer <= 0:
                    self.show_level_up = False
            return
        
        # Check for level up
        self.check_level_up()
        
        # Update level up display timer
        if self.show_level_up:
            self.level_up_timer -= 1
            if self.level_up_timer <= 0:
                self.show_level_up = False
        
        # Handle continuous key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:  # Add support for 'A' key
            self.player.move_left()
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # Add support for 'D' key
            self.player.move_right()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.is_off_screen():
                self.bullets.remove(bullet)
        
        # Spawn asteroids based on current level
        self.asteroid_spawn_timer += 1
        current_spawn_rate = self.get_spawn_rate()
        if self.asteroid_spawn_timer >= current_spawn_rate:
            asteroid_x = random.randint(0, SCREEN_WIDTH - ASTEROID_WIDTH)
            # Pass current level to asteroid constructor
            self.asteroids.append(Asteroid(asteroid_x, -ASTEROID_HEIGHT, self.get_current_level()))
            self.asteroid_spawn_timer = 0
        
        # Spawn enemy ships occasionally
        if random.random() < ENEMY_SHIP_SPAWN_CHANCE * (1 + self.get_current_level() * 0.2):
            enemy_x = random.randint(0, SCREEN_WIDTH - ENEMY_SHIP_WIDTH)
            self.enemy_ships.append(EnemyShip(enemy_x, -ENEMY_SHIP_HEIGHT, self.get_current_level()))
        
        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update()
            if asteroid.is_off_screen():
                self.asteroids.remove(asteroid)
        
        # Update enemy ships and handle their shooting
        for enemy in self.enemy_ships[:]:
            enemy.update()
            if enemy.is_off_screen():
                self.enemy_ships.remove(enemy)
            elif enemy.can_shoot():
                # Enemy shoots at player
                enemy_bullet = enemy.shoot()
                self.enemy_bullets.append(enemy_bullet)
        
        # Update enemy bullets
        for enemy_bullet in self.enemy_bullets[:]:
            enemy_bullet.update()
            if enemy_bullet.is_off_screen():
                self.enemy_bullets.remove(enemy_bullet)
        
        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # Check bullet-asteroid collisions
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    # Create explosion particles
                    for _ in range(8):
                        self.particles.append(Particle(asteroid.x + asteroid.width // 2, 
                                                     asteroid.y + asteroid.height // 2))
                    
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    
                    # Score increases based on asteroid level
                    points = 10 * asteroid.level  # Higher level asteroids give more points
                    self.score += points
                    
                    # Play explosion sound
                    if self.audio_enabled and 'explosion' in self.sounds:
                        explosion_channel = pygame.mixer.Channel(2)
                        explosion_channel.play(self.sounds['explosion'])
                        explosion_channel.set_volume(0.6)
                    break
        
        # Check bullet-enemy ship collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemy_ships[:]:
                if bullet.rect.colliderect(enemy.rect):
                    # Create explosion particles
                    for _ in range(6):
                        self.particles.append(Particle(enemy.x + enemy.width // 2, 
                                                     enemy.y + enemy.height // 2))
                    
                    self.bullets.remove(bullet)
                    self.enemy_ships.remove(enemy)
                    
                    # Enemy ships give more points than asteroids
                    points = 25 * enemy.level
                    self.score += points
                    
                    # Play explosion sound
                    if self.audio_enabled and 'explosion' in self.sounds:
                        explosion_channel = pygame.mixer.Channel(2)
                        explosion_channel.play(self.sounds['explosion'])
                        explosion_channel.set_volume(0.7)
                    break
        
        # Check enemy bullet-player collisions
        for enemy_bullet in self.enemy_bullets[:]:
            if enemy_bullet.rect.colliderect(self.player.rect):
                self.enemy_bullets.remove(enemy_bullet)
                
                # Player takes damage (check shield)
                if self.player.take_damage():
                    # Create big explosion
                    for _ in range(15):
                        self.particles.append(Particle(self.player.x + self.player.width // 2, 
                                                     self.player.y + self.player.height // 2))
                    
                    self.game_over = True
                    if self.score > self.high_score:
                        self.high_score = self.score
                    
                    # Play explosion sound for game over
                    if self.audio_enabled and 'explosion' in self.sounds:
                        game_over_channel = pygame.mixer.Channel(3)
                        game_over_channel.play(self.sounds['explosion'])
                        game_over_channel.set_volume(1.0)
                    
                    # Stop background music when game over
                    if self.music_channel and self.music_playing:
                        self.music_channel.stop()
                        self.music_playing = False
                else:
                    # Shield absorbed the hit - create small explosion
                    for _ in range(5):
                        self.particles.append(Particle(self.player.x + self.player.width // 2, 
                                                     self.player.y + self.player.height // 2))
                break
        
        # Check player-asteroid collisions
        for asteroid in self.asteroids:
            if self.player.rect.colliderect(asteroid.rect):
                # Create big explosion
                for _ in range(15):
                    self.particles.append(Particle(self.player.x + self.player.width // 2, 
                                                 self.player.y + self.player.height // 2))
                
                self.game_over = True
                if self.score > self.high_score:
                    self.high_score = self.score
                
                # Play explosion sound for game over
                if self.audio_enabled and 'explosion' in self.sounds:
                    game_over_channel = pygame.mixer.Channel(3)
                    game_over_channel.play(self.sounds['explosion'])
                    game_over_channel.set_volume(1.0)
                
                # Stop background music when game over
                if self.music_channel and self.music_playing:
                    self.music_channel.stop()
                    self.music_playing = False
    
    def draw_stars(self):
        """Draw scrolling star field"""
        for i, (x, y) in enumerate(self.stars):
            pygame.draw.circle(self.screen, WHITE, (x, y), 1)
            # Move stars down slowly
            self.stars[i] = (x, (y + 1) % SCREEN_HEIGHT)
    
    def draw(self):
        """Draw all game objects"""
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw star field
        self.draw_stars()
        
        if not self.game_over:
            # Draw game objects
            self.player.draw(self.screen)
            
            for bullet in self.bullets:
                bullet.draw(self.screen)
            
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)
            
            for enemy in self.enemy_ships:
                enemy.draw(self.screen)
            
            for enemy_bullet in self.enemy_bullets:
                enemy_bullet.draw(self.screen)
            
            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen)
            
            # Draw score, level, and high score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            level_text = self.font.render(f"Level: {self.get_current_level()}", True, GREEN)
            high_score_text = self.small_font.render(f"High Score: {self.high_score}", True, YELLOW)
            
            # Display difficulty info
            spawn_rate = self.get_spawn_rate()
            difficulty_text = self.small_font.render(f"Spawn Rate: {spawn_rate} | Speed: x{1 + (self.get_current_level() - 1) * 0.3:.1f}", True, WHITE)
            
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(level_text, (10, 50))
            self.screen.blit(high_score_text, (10, 90))
            self.screen.blit(difficulty_text, (10, 120))
            
            # Draw level up message
            if self.show_level_up:
                level_up_text = self.big_font.render(f"LEVEL {self.level}!", True, YELLOW)
                level_up_rect = level_up_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                
                # Add a semi-transparent background
                overlay = pygame.Surface((level_up_text.get_width() + 40, level_up_text.get_height() + 20))
                overlay.set_alpha(180)
                overlay.fill(BLACK)
                overlay_rect = overlay.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                self.screen.blit(overlay, overlay_rect)
                self.screen.blit(level_up_text, level_up_rect)
            
            # Draw instructions
            instruction_text = self.small_font.render("Arrow Keys: Move | Space: Shoot | M: Toggle Music", True, WHITE)
            self.screen.blit(instruction_text, (10, SCREEN_HEIGHT - 30))
            
            # Draw music status
            if self.audio_enabled:
                music_status = "Music: ON" if self.music_playing else "Music: OFF"
                music_text = self.small_font.render(music_status, True, GREEN if self.music_playing else RED)
                self.screen.blit(music_text, (SCREEN_WIDTH - 100, 10))
        
        else:
            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen)
            
            # Draw game over screen
            game_over_text = self.big_font.render("GAME OVER", True, RED)
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            high_score_text = self.font.render(f"High Score: {self.high_score}", True, YELLOW)
            restart_text = self.font.render("Press R to Restart or Close Window to Quit", True, WHITE)
            
            # Center the text
            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
            
            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(final_score_text, score_rect)
            self.screen.blit(high_score_text, high_score_rect)
            self.screen.blit(restart_text, restart_rect)
        
        # Update display
        pygame.display.flip()
    
    def restart_game(self):
        """Restart the game"""
        self.game_over = False
        self.score = 0
        self.level = 1
        self.previous_level = 1
        self.show_level_up = False
        self.level_up_timer = 0
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - PLAYER_HEIGHT - 10)
        self.bullets = []
        self.asteroids = []
        self.particles = []
        self.asteroid_spawn_timer = 0
        
        # Restart background music
        if self.audio_enabled and 'music' in self.sounds and self.music_channel:
            self.music_channel.play(self.sounds['music'], loops=-1)
            self.music_channel.set_volume(0.2)
            self.music_playing = True
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        # Clean up audio
        if self.audio_enabled:
            pygame.mixer.stop()
        
        pygame.quit()
        sys.exit()

def main():
    """Main function to start the game"""
    print("=" * 60)
    print("🚀 SPACE SHOOTER - ENHANCED EDITION WITH LEVELS 🚀")
    print("=" * 60)
    print("Controls:")
    print("- Left/Right Arrow Keys: Move spaceship")
    print("- Spacebar: Shoot bullets")
    print("- M: Toggle background music on/off")
    print("- R: Restart game (when game over)")
    print("- Close window: Quit game")
    print("\nFeatures:")
    print("✨ Background music (procedurally generated)")
    print("💥 Sound effects for shooting and explosions")
    print("🎆 Particle explosion effects")
    print("⭐ Scrolling star field background")
    print("🏆 High score tracking")
    print("🎵 Music toggle functionality")
    print("📈 Progressive level system")
    print("\nLevel System:")
    print(f"- Advance 1 level every {POINTS_PER_LEVEL} points")
    print("- Higher levels = faster asteroids + more frequent spawning")
    print("- Higher level asteroids give more points")
    print("- Visual indicators show asteroid difficulty")
    print(f"- Maximum level: {MAX_LEVEL}")
    print("\nObjective: Destroy asteroids to increase your score!")
    print("Survive as long as possible as difficulty increases!")
    print("=" * 60)
    
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
