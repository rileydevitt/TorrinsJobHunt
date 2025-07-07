import pygame
import random
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.25
FLAP_STRENGTH = -7
PIPE_SPEED = 3
PIPE_GAP = 200
PIPE_FREQUENCY = 1500  # milliseconds
PIPE_WIDTH = 100
TEXTURE_HEIGHT = 60
BIRD_SIZE = 30
BIRD_HITBOX_SIZE = 12

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
SKY_BLUE = (135, 206, 235)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Torrin's Job Hunt")
clock = pygame.time.Clock()

# Load background image
def load_background():
    try:
        background = pygame.image.load("linkedin.pdf")
        # Scale the background to fit the screen
        return pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    except Exception as e:
        print(f"Error loading background: {e}")
        return None

# Load and prepare pipe texture
def load_pipe_texture():
    try:
        # Try to load the PDF as an image
        original_texture = pygame.image.load("Employment-Job-Application.pdf")
        # Scale down the texture to a smaller size for tiling
        texture = pygame.transform.scale(original_texture, (PIPE_WIDTH, TEXTURE_HEIGHT))
    except:
        # If loading fails, create a default texture
        texture = pygame.Surface((PIPE_WIDTH, TEXTURE_HEIGHT))
        texture.fill(GREEN)
        # Add some visual interest to the default texture
        for i in range(0, TEXTURE_HEIGHT, 5):
            pygame.draw.line(texture, (0, 200, 0), (0, i), (PIPE_WIDTH, i), 1)
    return texture

# Load bird image
def load_bird_image():
    try:
        # Print current directory for debugging
        print(f"Current directory: {os.getcwd()}")
        print(f"Files in directory: {os.listdir('.')}")
        
        # Try loading with the exact filename
        image = pygame.image.load("torrin.pdf")
        print("Successfully loaded bird image!")
        # Scale the image to a smaller size for the bird
        return pygame.transform.scale(image, (BIRD_SIZE * 2, BIRD_SIZE * 2))
    except Exception as e:
        print(f"Error loading bird image: {e}")
        return None

PIPE_TEXTURE = load_pipe_texture()
BIRD_IMAGE = load_bird_image()
BACKGROUND_IMAGE = load_background()

class Bird:
    def __init__(self):
        self.x = SCREEN_WIDTH // 3
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = BIRD_SIZE
        self.hitbox_size = BIRD_HITBOX_SIZE
        self.rotation = 0  # Add rotation for the bird

    def flap(self):
        self.velocity = FLAP_STRENGTH
        self.rotation = -30  # Rotate up when flapping

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        # Gradually rotate back to horizontal
        if self.rotation < 0:
            self.rotation += 2

    def draw(self):
        if BIRD_IMAGE:
            # Create a rotated copy of the image
            rotated_image = pygame.transform.rotate(BIRD_IMAGE, self.rotation)
            # Get the rect of the rotated image
            image_rect = rotated_image.get_rect(center=(self.x, int(self.y)))
            # Draw the rotated image
            screen.blit(rotated_image, image_rect)
        else:
            # Fallback to circle if image loading failed
            pygame.draw.circle(screen, BLUE, (self.x, int(self.y)), self.size)
            print("Using fallback circle for bird")
        
        # Uncomment the next line to see the hitbox (for debugging)
        # pygame.draw.circle(screen, (255, 0, 0), (self.x, int(self.y)), self.hitbox_size, 1)

    def get_rect(self):
        # Return a smaller hitbox than the visual size
        return pygame.Rect(self.x - self.hitbox_size, 
                         self.y - self.hitbox_size, 
                         self.hitbox_size * 2, 
                         self.hitbox_size * 2)

class Pipe:
    def __init__(self):
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 100)
        self.x = SCREEN_WIDTH
        self.width = PIPE_WIDTH
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self):
        # Draw top pipe
        top_height = self.gap_y - PIPE_GAP // 2
        top_pipe = pygame.Surface((self.width, top_height))
        # Tile the texture multiple times
        for y in range(0, top_height, TEXTURE_HEIGHT):
            top_pipe.blit(PIPE_TEXTURE, (0, y))
        screen.blit(top_pipe, (self.x, 0))

        # Draw bottom pipe
        bottom_height = SCREEN_HEIGHT - (self.gap_y + PIPE_GAP // 2)
        bottom_pipe = pygame.Surface((self.width, bottom_height))
        # Tile the texture multiple times
        for y in range(0, bottom_height, TEXTURE_HEIGHT):
            bottom_pipe.blit(PIPE_TEXTURE, (0, y))
        screen.blit(bottom_pipe, (self.x, self.gap_y + PIPE_GAP // 2))

    def get_rects(self):
        top_pipe = pygame.Rect(self.x, 0, self.width, self.gap_y - PIPE_GAP // 2)
        bottom_pipe = pygame.Rect(self.x, self.gap_y + PIPE_GAP // 2,
                                self.width, SCREEN_HEIGHT)
        return top_pipe, bottom_pipe

class Game:
    def __init__(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.last_pipe = pygame.time.get_ticks()
        self.font = pygame.font.Font(None, 36)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not self.game_over:
                    self.bird.flap()
                elif event.key == pygame.K_r and self.game_over:
                    self.__init__()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

    def update(self):
        if not self.game_over:
            self.bird.update()

            # Generate new pipes
            current_time = pygame.time.get_ticks()
            if current_time - self.last_pipe > PIPE_FREQUENCY:
                self.pipes.append(Pipe())
                self.last_pipe = current_time

            # Update pipes
            for pipe in self.pipes[:]:
                pipe.update()
                if pipe.x + pipe.width < 0:
                    self.pipes.remove(pipe)
                if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                    pipe.passed = True
                    self.score += 1

            # Check collisions
            if (self.bird.y < 0 or 
                self.bird.y > SCREEN_HEIGHT):  # Removed GROUND_HEIGHT check
                self.game_over = True

            for pipe in self.pipes:
                top_pipe, bottom_pipe = pipe.get_rects()
                if (self.bird.get_rect().colliderect(top_pipe) or 
                    self.bird.get_rect().colliderect(bottom_pipe)):
                    self.game_over = True

    def draw(self):
        # Draw background
        if BACKGROUND_IMAGE:
            screen.blit(BACKGROUND_IMAGE, (0, 0))
        else:
            screen.fill(SKY_BLUE)
        
        # Draw pipes
        for pipe in self.pipes:
            pipe.draw()

        # Draw bird
        self.bird.draw()

        # Draw score
        score_text = self.font.render(f'Score: {self.score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            # Create a semi-transparent black overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(200)  # Set transparency (0-255)
            screen.blit(overlay, (0, 0))
            
            game_over_text = self.font.render('You Found a J*b </3!', True, SKY_BLUE)
            restart_text = self.font.render('Press R to restart', True, SKY_BLUE)
            
            # Draw game over message
            screen.blit(game_over_text, 
                       (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                        SCREEN_HEIGHT // 2 - 20))
            
            # Draw restart instruction below
            screen.blit(restart_text,
                       (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                        SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

def main():
    game = Game()
    
    while True:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(60)

if __name__ == '__main__':
    main() 